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


class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "checkout"
        self.remote = self.base / "origin.git"
        self.upstream = self.base / "upstream.git"
        self.real_run = subprocess.run
        self.commands = []
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
        result = self.real_run(["git", "-C", str(cwd or self.repo), *map(str, args)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def intercept(self, command, **kwargs):
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

    def test_cloud_creates_missing_branches(self):
        self.work()
        self.g("branch", "-D", "master")
        tip = self.g("rev-parse", "work")
        result = self.prepare(cloud=True)
        self.assertEqual(result["created"], ["new-features", "master"])
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


if __name__ == "__main__":
    unittest.main()
