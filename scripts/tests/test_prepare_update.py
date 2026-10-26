"""Offline integration tests: HTTPS URLs are validated, fetches use local bare repos."""
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import prepare_update as helper

NATIVE_GIT = helper.resolve_git(Path(__file__).resolve().parents[2])


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "checkout with spaces"
        self.remote = self.base / "origin.git"
        self.upstream = self.base / "upstream.git"
        self.real_run = subprocess.run
        self.commands = []
        resolver = patch.object(helper, "resolve_git", return_value=NATIVE_GIT)
        self.resolver = resolver.start()
        self.addCleanup(resolver.stop)
        self.environment = patch.dict(os.environ, {"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
                                                   "GIT_TERMINAL_PROMPT": "0", "MINILOOT_MAINTENANCE_HOST": "codex-cloud"})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.g("init", "--bare", str(self.remote), cwd=self.base)
        self.g("init", "--bare", str(self.upstream), cwd=self.base)
        self.g("init", "-b", "new-features", str(self.repo), cwd=self.base)
        self.g("config", "user.name", "Workflow Test")
        self.g("config", "user.email", "test@example.invalid")
        (self.repo / "fixture").write_text("base\n")
        self.g("add", "fixture")
        self.g("commit", "-m", "Base")
        self.g("branch", "master")
        for destination in (self.remote, self.upstream):
            self.g("push", str(destination), "new-features", "master")
        self.g("remote", "add", "origin", helper.ORIGIN)
        self.g("remote", "add", "upstream", helper.UPSTREAM)
        self.g("config", "remote.origin.fetch", "+refs/heads/work:refs/remotes/origin/work")
        self.runner = patch.object(helper.subprocess, "run", side_effect=self.intercept)
        self.runner.start()
        self.addCleanup(self.runner.stop)
        # Simulate Linux without changing pathlib's host-specific path behavior.
        self.host = patch.object(helper, "os", type("Host", (), {"name": "posix", "environ": os.environ}))
        self.host.start()
        self.addCleanup(self.host.stop)

    def g(self, *args, cwd=None):
        result = self.real_run([NATIVE_GIT, "-C", str(cwd or self.repo), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def intercept(self, command, **kwargs):
        self.assertEqual(command[:3], [NATIVE_GIT, "-C", str(self.repo.resolve())])
        self.commands.append(command[3:])
        if command[3] == "fetch":
            command = list(command)
            index = command.index("origin") if "origin" in command else command.index("upstream")
            command[index] = str(self.remote if command[index] == "origin" else self.upstream)
        return self.real_run(command, **kwargs)

    def prepare(self, mode="update", cloud=False):
        return helper.prepare(mode, cloud, self.repo)

    def work(self):
        self.g("switch", "-c", "work")
        self.g("branch", "-D", "new-features")

    def commit(self):
        (self.repo / "fixture").write_text("changed\n")
        self.g("add", "fixture")
        self.g("commit", "-m", "Changed")

    def test_clean_and_narrow_fetch(self):
        result = self.prepare()
        self.assertEqual(result["behind"], {"new-features": 0, "master": 0})
        self.assertEqual(self.g("config", "remote.origin.fetch"), "+refs/heads/work:refs/remotes/origin/work")
        self.assertEqual(self.g("config", "branch.new-features.remote"), "origin")
        self.assertEqual(self.g("config", "branch.new-features.merge"), "refs/heads/new-features")
        self.assertFalse({"merge", "reset", "commit", "push"} & {c[0] for c in self.commands})

    def test_healthy_invocation_counts(self):
        for mode, expected in (("update", 23), ("development", 13)):
            with self.subTest(mode=mode):
                self.commands.clear()
                self.prepare(mode)
                self.assertEqual(len(self.commands), expected)
                self.assertEqual(sum(c[0] == "for-each-ref" for c in self.commands), 1)
                self.assertEqual(self.commands.count(["remote"]), int(mode == "update"))
                for flag in ([], ["--push"]):
                    self.assertIn(["remote", "get-url", *flag, "--all", "origin"], self.commands)

    def test_each_unfinished_marker(self):
        for marker in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply", "sequencer"):
            with self.subTest(marker=marker):
                path = Path(self.g("rev-parse", "--git-path", marker))
                path = path if path.is_absolute() else self.repo / path
                path.touch()
                try:
                    self.commands.clear()
                    with self.assertRaisesRegex(helper.PreparationError, "Unfinished"):
                        self.prepare()
                    self.assertEqual(len(self.commands), 3)
                finally:
                    path.unlink()

    def test_invalid_marker_responses(self):
        for output, code in (("", 0), ("one\ntwo", 0), ("\n".join(["same"] * 6), 0),
                             ("a\nb\n\nd\ne\nf", 0), ("a\nb\nc\nd\ne\nf\ng", 0), ("", 128)):
            with self.subTest(output=output, code=code):
                def response(command, **kwargs):
                    if command[3:5] == ["rev-parse", "--git-path"]:
                        return subprocess.CompletedProcess(command, code, output, "marker failure")
                    return self.intercept(command, **kwargs)
                self.commands.clear()
                with patch.object(helper.subprocess, "run", side_effect=response):
                    with self.assertRaises(helper.PreparationError):
                        self.prepare()
                self.assertFalse(any(c[0] in ("fetch", "remote", "config", "branch", "switch") for c in self.commands))

    def test_grouped_paths_match_individual_queries_in_worktree(self):
        worktree = self.base / "linked worktree with spaces"
        self.g("worktree", "add", "--detach", str(worktree))
        markers = ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply", "sequencer")
        for checkout in (self.repo, worktree):
            with self.subTest(checkout=checkout):
                individual = [self.g("rev-parse", "--git-path", m, cwd=checkout) for m in markers]
                grouped = self.g("rev-parse", *(a for m in markers for a in ("--git-path", m)), cwd=checkout).splitlines()
                self.assertEqual(grouped, individual)

    def test_absolute_marker_paths(self):
        original = self.intercept
        def absolute_paths(command, **kwargs):
            result = original(command, **kwargs)
            if command[3:5] == ["rev-parse", "--git-path"]:
                paths = [Path(value) for value in result.stdout.splitlines()]
                result.stdout = "\n".join(str(p if p.is_absolute() else self.repo / p) for p in paths)
            return result
        with patch.object(helper.subprocess, "run", side_effect=absolute_paths):
            self.prepare("development")

    def test_origin_wrong_push_in_both_modes(self):
        self.g("remote", "set-url", "--push", "origin", "https://example.invalid/repo")
        for mode in ("update", "development"):
            with self.subTest(mode=mode):
                self.commands.clear()
                with self.assertRaisesRegex(helper.PreparationError, "origin URL"):
                    self.prepare(mode)
                self.assertFalse(any(c[0] == "fetch" for c in self.commands))

    def test_cloud_creates_missing_branches(self):
        self.work()
        self.g("branch", "-D", "master")
        tip = self.g("rev-parse", "work")
        result = self.prepare(cloud=True)
        self.assertEqual(result["created"], ["new-features", "master"])
        self.assertEqual(result["local_tips"], {name: self.g("rev-parse", name) for name in ("new-features", "master")})
        self.assertEqual(self.g("branch", "--show-current"), "new-features")
        self.assertEqual(self.g("rev-parse", "work"), tip)
        self.assertEqual(self.g("config", "branch.master.remote"), "origin")
        self.assertEqual(self.g("config", "branch.master.merge"), "refs/heads/master")

    def test_rewritten_remote_refreshes_tracking_and_preserves_local(self):
        base = self.g("rev-parse", "new-features")
        self.commit()
        local_tip = self.g("rev-parse", "new-features")
        self.g("push", str(self.remote), "new-features")
        self.prepare("development")
        self.assertEqual(self.g("rev-parse", "origin/new-features"), local_tip)
        # Rewrite only the temporary bare remote, never the local project branch.
        self.g("update-ref", "refs/heads/new-features", base, local_tip, cwd=self.remote)
        self.commands.clear()
        with self.assertRaisesRegex(helper.PreparationError, "new-features has unpublished/divergent"):
            self.prepare("development")
        self.assertEqual(self.g("rev-parse", "origin/new-features"), base)
        self.assertEqual(self.g("rev-parse", "new-features"), local_tip)
        self.assertEqual(self.g("branch", "--show-current"), "new-features")
        self.assertEqual(self.g("status", "--porcelain=v1"), "")
        self.assertIn(["fetch", "--no-tags", "origin",
                       "+refs/heads/new-features:refs/remotes/origin/new-features"], self.commands)
        self.assertFalse({"merge", "reset", "commit", "push"} & {c[0] for c in self.commands})
        self.assertFalse(any(c[0] in ("branch", "switch", "config") for c in self.commands))

    def test_origin_wrong(self):
        self.g("remote", "set-url", "origin", "https://example.invalid/repo")
        with self.assertRaisesRegex(helper.PreparationError, "origin URL"):
            self.prepare()
        self.assertFalse(any(c[0] == "fetch" for c in self.commands))

    def test_upstream_wrong(self):
        self.g("remote", "set-url", "upstream", "https://example.invalid/repo")
        with self.assertRaisesRegex(helper.PreparationError, "upstream URL"):
            self.prepare()

    def test_missing_upstream_update(self):
        self.g("remote", "remove", "upstream")
        self.prepare()
        self.assertEqual(self.g("remote", "get-url", "upstream"), helper.UPSTREAM)

    def test_development_does_not_touch_upstream_master(self):
        self.g("remote", "remove", "upstream")
        master = self.g("rev-parse", "master")
        self.prepare("development")
        self.assertEqual(self.g("remote"), "origin")
        self.assertEqual(self.g("rev-parse", "master"), master)
        self.assertFalse(any("master" in " ".join(c) or "upstream" in " ".join(c) for c in self.commands))

    def test_dirty_before_mutation(self):
        (self.repo / "untracked").write_text("dirty")
        with self.assertRaisesRegex(helper.PreparationError, "Dirty"):
            self.prepare()
        self.assertFalse(any(c[0] in ("fetch", "branch", "switch", "remote") for c in self.commands))

    def test_unpublished_work_preserved(self):
        self.work()
        self.commit()
        tip = self.g("rev-parse", "work")
        with self.assertRaisesRegex(helper.PreparationError, "work has"):
            self.prepare(cloud=True)
        self.assertEqual(self.g("branch", "--show-current"), "work")
        self.assertEqual(self.g("rev-parse", "work"), tip)
        self.assertFalse(any(c[0] in ("branch", "switch") for c in self.commands))

    def test_divergent_work(self):
        self.g("switch", "-c", "work")
        self.commit()
        self.g("switch", "new-features")
        (self.repo / "other").write_text("origin advance")
        self.g("add", "other")
        self.g("commit", "-m", "Other")
        self.g("push", str(self.remote), "new-features")
        self.g("switch", "work")
        with self.assertRaisesRegex(helper.PreparationError, "work has"):
            self.prepare(cloud=True)
        self.assertEqual(self.g("branch", "--show-current"), "work")

    def test_cloud_requires_authorization(self):
        with patch.dict(os.environ, {"MINILOOT_MAINTENANCE_HOST": ""}):
            with self.assertRaisesRegex(helper.PreparationError, "explicitly authorized"):
                self.prepare(cloud=True)

    def test_windows_rejects_cloud_work(self):
        with patch.object(helper, "os", type("Host", (), {"name": "nt", "environ": os.environ})), patch.object(helper, "WINDOWS_ROOT", self.repo):
            with self.assertRaisesRegex(helper.PreparationError, "non-Windows"):
                self.prepare(cloud=True)

    def test_unsafe_master(self):
        self.g("switch", "master")
        self.commit()
        self.g("push", str(self.remote), "master")
        self.g("switch", "new-features")
        with self.assertRaisesRegex(helper.PreparationError, "safe upstream-only"):
            self.prepare()
        self.assertFalse(any(c[0] in ("branch", "switch") for c in self.commands))

    def test_local_unpublished_history(self):
        self.commit()
        with self.assertRaisesRegex(helper.PreparationError, "new-features has"):
            self.prepare()

    def test_existing_behind_branch_is_preserved(self):
        initial = self.g("rev-parse", "new-features")
        self.commit()
        self.g("push", str(self.remote), "new-features")
        self.g("switch", "--detach", initial)
        self.g("branch", "-f", "new-features", initial)
        self.g("switch", "new-features")
        result = self.prepare()
        self.assertEqual(result["behind"]["new-features"], 1)
        self.assertEqual(self.g("rev-parse", "new-features"), initial)
        self.assertEqual(result["local_tips"]["new-features"], initial)

    def test_grouped_tips_preserve_json_contract(self):
        for mode in ("update", "development"):
            with self.subTest(mode=mode):
                result = self.prepare(mode)
                names = ["new-features"] + (["master"] if mode == "update" else [])
                refs = ["origin/" + name for name in names] + (["upstream/master"] if mode == "update" else [])
                self.assertEqual(set(result), {"root", "mode", "branch", "created", "refs", "behind", "local_tips"})
                self.assertEqual(result["root"], str(self.repo.resolve()))
                self.assertEqual(result["mode"], mode)
                self.assertEqual(result["branch"], "new-features")
                self.assertEqual(result["created"], [])
                self.assertEqual(result["refs"], {ref: self.g("rev-parse", "--verify", "refs/remotes/" + ref) for ref in refs})
                self.assertEqual(result["local_tips"], {name: self.g("rev-parse", "--verify", "refs/heads/" + name) for name in names})
                self.assertEqual(result["behind"], dict.fromkeys(names, 0))

    def test_invalid_grouped_reference_responses(self):
        for mode in ("update", "development"):
            for case in ("empty", "missing", "duplicate", "extra", "prefix", "short", "nonhex", "long", "columns", "blank"):
                with self.subTest(mode=mode, case=case):
                    def response(command, **kwargs):
                        result = self.intercept(command, **kwargs)
                        if command[3] == "for-each-ref":
                            lines = result.stdout.splitlines()
                            ref, sha = lines[0].split("\t")
                            if case == "empty": lines = []
                            elif case == "missing": lines.pop()
                            elif case == "duplicate": lines.append(lines[0])
                            elif case == "extra": lines.append("refs/heads/work\t" + sha)
                            elif case == "prefix": lines[0] = ref + "/unexpected\t" + sha
                            elif case == "short": lines[0] = ref + "\t" + sha[:-1]
                            elif case == "nonhex": lines[0] = ref + "\t" + "z" * 40
                            elif case == "long": lines[0] = ref + "\t" + sha + "0"
                            elif case == "columns": lines[0] += "\textra"
                            elif case == "blank": lines.insert(1, "")
                            result.stdout = "\n".join(lines)
                        return result
                    with patch.object(helper.subprocess, "run", side_effect=response):
                        with self.assertRaises(helper.PreparationError):
                            self.prepare(mode)

    def test_grouped_reference_failure(self):
        def response(command, **kwargs):
            if command[3] == "for-each-ref":
                return subprocess.CompletedProcess(command, 128, "", "reference failure")
            return self.intercept(command, **kwargs)
        with patch.object(helper.subprocess, "run", side_effect=response):
            with self.assertRaisesRegex(helper.PreparationError, "reference failure"):
                self.prepare()

    def test_grouped_reference_order_is_irrelevant(self):
        def response(command, **kwargs):
            result = self.intercept(command, **kwargs)
            if command[3] == "for-each-ref":
                result.stdout = "\n".join(reversed(result.stdout.splitlines()))
            return result
        with patch.object(helper.subprocess, "run", side_effect=response):
            result = self.prepare()
        self.assertEqual(result["local_tips"], {name: self.g("rev-parse", name) for name in ("new-features", "master")})

    def test_cloud_development_tips_exclude_work_and_master(self):
        self.work()
        work = self.g("rev-parse", "work")
        master = self.g("rev-parse", "master")
        result = self.prepare("development", cloud=True)
        self.assertEqual(result["local_tips"], {"new-features": self.g("rev-parse", "new-features")})
        self.assertEqual(result["created"], ["new-features"])
        self.assertEqual(self.g("rev-parse", "work"), work)
        self.assertEqual(self.g("rev-parse", "master"), master)

    def test_zero_behind_does_not_prove_upstream_ancestry(self):
        self.g("switch", "master")
        self.commit()
        self.g("push", str(self.remote), "master")
        self.g("push", str(self.upstream), "master")
        self.g("switch", "new-features")
        result = self.prepare()
        self.assertEqual(result["behind"], {"new-features": 0, "master": 0})
        check = self.real_run([NATIVE_GIT, "-C", str(self.repo), "merge-base", "--is-ancestor",
                               result["refs"]["upstream/master"], result["local_tips"]["new-features"]],
                              capture_output=True, text=True)
        self.assertEqual(check.returncode, 1, check.stderr)

    def test_local_tip_baseline_requires_refresh_after_fast_forward(self):
        initial = self.g("rev-parse", "new-features")
        self.commit()
        advanced = self.g("rev-parse", "new-features")
        self.g("push", str(self.remote), "new-features")
        self.g("switch", "--detach", initial)
        self.g("branch", "-f", "new-features", initial)
        self.g("switch", "new-features")
        baseline = self.prepare("development")
        self.assertEqual(baseline["local_tips"]["new-features"], initial)
        self.assertEqual(baseline["refs"]["origin/new-features"], advanced)
        self.g("merge", "--ff-only", "origin/new-features")
        self.assertNotEqual(baseline["local_tips"]["new-features"], self.g("rev-parse", "new-features"))
        refreshed_tip = self.g("rev-parse", "refs/heads/new-features")
        self.assertEqual(refreshed_tip, advanced)


    def test_git_failure_diagnostics_stop_immediately(self):
        cases = [
            (128, "", "Could not resolve host: github.com"),
            (128, "", "Could not resolve proxy: proxy.invalid"),
            (128, "", "Authentication failed"),
            (128, "", ""), (128, "stdout detail", ""),
            (128, "", "stderr detail"), (128, "out", "err"),
            (7, "unexpected", "failure"),
        ]
        for code, out, err in cases:
            with self.subTest(code=code, out=out, err=err):
                with patch.object(helper.subprocess, "run", return_value=
                                  subprocess.CompletedProcess([], code, out, err)) as run:
                    with self.assertRaises(helper.PreparationError) as caught:
                        self.prepare()
                message = str(caught.exception)
                self.assertIn("git rev-parse --show-toplevel", message)
                self.assertIn("exited " + str(code), message)
                for name, value in (("stdout", out), ("stderr", err)):
                    if value:
                        self.assertIn(name + "=", message)
                        self.assertIn(value, message)
                if not out and not err:
                    self.assertIn("stdout and stderr are empty", message)
                self.assertEqual(run.call_count, 1)

    def test_fetch_failures_have_no_retry_or_continuation(self):
        for out, err in (("", "Could not resolve host: github.com"),
                         ("", "Could not resolve proxy: proxy.invalid"),
                         ("", "Authentication failed"), ("", ""),
                         ("output only", ""), ("out", "err"),
                         ("https://user:secret@github.com/repo?key=hidden", "token=private"),
                         ("x" * 10000, "y" * 10000)):
            with self.subTest(out=out[:30], err=err[:30]):
                seen = []
                def response(command, **kwargs):
                    seen.append(command[3])
                    if command[3] == "fetch":
                        return subprocess.CompletedProcess(command, 128, out, err)
                    return self.intercept(command, **kwargs)
                with patch.object(helper.subprocess, "run", side_effect=response):
                    with self.assertRaises(helper.PreparationError) as caught:
                        self.prepare()
                message = str(caught.exception)
                self.assertIn("git fetch --no-tags origin", message)
                self.assertIn("exited 128", message)
                self.assertEqual(seen.count("fetch"), 1)
                self.assertEqual(seen[-1], "fetch")
                self.assertFalse({"config", "branch", "switch", "merge", "push"} & set(seen))
                for secret in ("user:secret", "hidden", "private"):
                    self.assertNotIn(secret, message)
                self.assertLess(len(message), 5000)

    def test_git_launch_failure(self):
        with patch.object(helper.subprocess, "run", side_effect=FileNotFoundError("missing Git")) as run:
            with self.assertRaisesRegex(helper.PreparationError, "Could not start.*git rev-parse"):
                self.prepare()
        self.assertEqual(run.call_count, 1)

    def test_allowed_one_and_unexpected_history_codes(self):
        for operation in ("merge-base", "show-ref"):
            for code in (1, 128):
                with self.subTest(operation=operation, code=code):
                    seen = []
                    def response(command, **kwargs):
                        seen.append(command[3])
                        if command[3] == operation:
                            return subprocess.CompletedProcess(command, code, "", "")
                        return self.intercept(command, **kwargs)
                    with patch.object(helper.subprocess, "run", side_effect=response):
                        if operation == "show-ref" and code == 1:
                            self.work()
                            self.assertEqual(self.prepare("development", cloud=True)["created"], ["new-features"])
                        else:
                            with self.assertRaises(helper.PreparationError) as caught:
                                self.prepare("development")
                            if code == 128:
                                self.assertIn("exited 128", str(caught.exception))
                            else:
                                self.assertIn("unpublished/divergent", str(caught.exception))
                            self.assertEqual(seen[-1], operation)

    def test_resolution_is_once_per_preparation(self):
        self.resolver.reset_mock()
        self.prepare("development")
        self.resolver.assert_called_once_with(self.repo.resolve())

    def test_cli_failure_json(self):
        import contextlib
        import io
        import json
        output = io.StringIO()
        with patch.object(sys, "argv", ["prepare_update.py"]), \
                patch.object(helper, "prepare", side_effect=helper.PreparationError("failed")), \
                contextlib.redirect_stdout(output):
            self.assertEqual(helper.main(), 1)
        self.assertEqual(json.loads(output.getvalue()), {"error": "failed"})


class DiagnosticTests(unittest.TestCase):
    def test_redaction_and_bounds(self):
        secrets = ["user:pass", "querysecret", "headersecret", "tokensecret", "ghp_abcdef123"]
        raw = ("https://user:pass@github.com/repo?key=querysecret "
               "token=tokensecret ghp_abcdef123\nAuthorization: Bearer headersecret\n"
               + "x" * 5000 + "\x1b[31m")
        result = helper.diagnostic(raw)
        for secret in secrets:
            self.assertNotIn(secret, result)
        self.assertIn("github.com/repo", result)
        self.assertIn("[REDACTED]", result)
        self.assertIn("[truncated]", result)
        self.assertLessEqual(len(result), 1600)
        self.assertNotIn("\x1b", result)

    def test_control_characters_and_short_credentials(self):
        result = helper.diagnostic('Proxy-Authorization: Basic abc\npassword="two words"\n\x1b[31m')
        self.assertNotIn("abc", result)
        self.assertNotIn("two words", result)
        self.assertIn(r"\u001b", result)
        self.assertNotIn("jsonsecret", helper.diagnostic('{"access_token": "jsonsecret"}'))


class GitSelectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "checkout"
        self.root.mkdir()
        self.git = self.base / "Git" / "cmd" / "git.exe"
        self.git.parent.mkdir(parents=True)
        self.git.touch()

    def test_resolution_failure_precedes_git(self):
        with patch.object(helper, "resolve_git", side_effect=helper.PreparationError("unavailable")), \
                patch.object(helper.subprocess, "run") as run:
            with self.assertRaisesRegex(helper.PreparationError, "unavailable"):
                helper.prepare(cwd=self.root)
        run.assert_not_called()

    def windows(self):
        return patch.object(helper, "os", type("Host", (), {"name": "nt"}))

    def test_windows_known_install_ignores_path(self):
        with self.windows(), patch.object(helper, "WINDOWS_GIT", self.git), \
                patch.object(helper.shutil, "which", side_effect=AssertionError("PATH consulted")), \
                patch.object(helper.subprocess, "run", side_effect=AssertionError("subprocess launched")):
            self.assertEqual(helper.resolve_git(self.root), str(self.git.resolve()))

    def test_windows_missing_directory_and_checkout_rejected(self):
        (self.root / "git.exe").touch()
        for candidate in (self.base / "missing.exe", self.git.parent, self.root / "git.exe"):
            with self.subTest(candidate=candidate):
                with self.windows(), patch.object(helper, "WINDOWS_GIT", candidate):
                    with self.assertRaises(helper.PreparationError):
                        helper.resolve_git(self.root)

    def test_linux_restricted_search_and_missing(self):
        with patch.object(helper, "os", type("Host", (), {"name": "posix"})), \
                patch.object(helper.sys, "platform", "linux"), \
                patch.object(helper.shutil, "which", return_value=None) as which, \
                patch.object(helper.subprocess, "run", side_effect=AssertionError("subprocess launched")):
            with self.assertRaisesRegex(helper.PreparationError, "not found"):
                helper.resolve_git(self.root)
            which.assert_called_once_with("git", path="/usr/bin:/bin:/usr/local/bin")

    def test_linux_permissions_and_checkout(self):
        from types import SimpleNamespace
        for uid, mode, accepted in ((0, 0o100755, True), (1000, 0o100755, False),
                                    (0, 0o100775, False), (0, 0o100777, False), (0, 0o100644, False)):
            with self.subTest(uid=uid, mode=mode):
                with patch.object(helper, "os", type("Host", (), {"name": "posix"})), \
                        patch.object(helper.sys, "platform", "linux"), \
                        patch.object(helper.shutil, "which", return_value=str(self.git)), \
                        patch.object(Path, "stat", return_value=SimpleNamespace(st_uid=uid, st_mode=mode)):
                    if accepted:
                        self.assertEqual(helper.resolve_git(self.root), str(self.git.resolve()))
                    else:
                        with self.assertRaises(helper.PreparationError):
                            helper.resolve_git(self.root)

    def test_windows_redirected_installation_rejected(self):
        with self.windows(), patch.object(helper, "WINDOWS_GIT", self.git), \
                patch.object(Path, "resolve", return_value=Path(NATIVE_GIT)):
            with self.assertRaisesRegex(helper.PreparationError, "outside its installation"):
                helper.resolve_git(self.root)

    def test_linux_writable_ancestor_rejected(self):
        from types import SimpleNamespace
        real_stat = Path.stat
        def attributes(path, *args, **kwargs):
            info = real_stat(path, *args, **kwargs)
            return SimpleNamespace(st_uid=0, st_mode=info.st_mode | (0o020 if path == self.git.parent else 0o111))
        with patch.object(helper, "os", type("Host", (), {"name": "posix"})), \
                patch.object(helper.sys, "platform", "linux"), \
                patch.object(helper.shutil, "which", return_value=str(self.git)), \
                patch.object(Path, "stat", attributes):
            with self.assertRaisesRegex(helper.PreparationError, "group/world-writable"):
                helper.resolve_git(self.root)
        with patch.object(helper, "os", type("Host", (), {"name": "posix"})), \
                patch.object(helper.sys, "platform", "linux"), \
                patch.object(helper.shutil, "which", return_value=str(self.root)):
            with self.assertRaisesRegex(helper.PreparationError, "inside the checkout"):
                helper.resolve_git(self.root)


if __name__ == "__main__":
    unittest.main()
