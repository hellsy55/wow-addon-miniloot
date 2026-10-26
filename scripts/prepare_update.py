"""Prepare maintenance refs and branches; never integrate or publish content."""
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys

ORIGIN = "https://github.com/hellsy55/wow-addon-miniloot.git"
UPSTREAM = "https://github.com/Vladinator/wow-addon-miniloot.git"
WINDOWS_ROOT = Path(r"C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot")
WINDOWS_GIT = Path(r"C:\Program Files\Git\cmd\git.exe")
LINUX_GIT_PATH = "/usr/bin:/bin:/usr/local/bin"


class PreparationError(RuntimeError):
    pass


def resolve_git(root):
    """Use the managed Windows install or a root-owned Linux system executable."""
    try:
        if os.name == "nt":
            candidate = WINDOWS_GIT
        elif sys.platform.startswith("linux"):
            found = shutil.which("git", path=LINUX_GIT_PATH)
            if not found:
                raise PreparationError("Trusted Git executable not found in Linux system directories")
            candidate = Path(found)
        else:
            raise PreparationError("Unsupported host for trusted Git selection")
        resolved = candidate.resolve(strict=True)
        if resolved == root or root in resolved.parents or not resolved.is_file():
            raise PreparationError("Trusted Git executable is invalid or inside the checkout")
        if os.name == "nt":
            # Do not follow a redirected installation outside the expected Git tree.
            if WINDOWS_GIT.parent.parent not in resolved.parents:
                raise PreparationError("Trusted Windows Git resolves outside its installation")
        else:
            if not resolved.stat().st_mode & 0o111:
                raise PreparationError("Trusted Git is not executable")
            for path in (resolved, *resolved.parents):
                info = path.stat()
                if info.st_uid != 0 or info.st_mode & (stat.S_IWGRP | stat.S_IWOTH):
                    raise PreparationError("Trusted Linux Git path must be root-owned and not group/world-writable")
        return str(resolved)
    except OSError as error:
        raise PreparationError("Trusted Git executable unavailable: " + diagnostic(error)) from None


def diagnostic(value):
    """Redact common credential forms before bounding and escaping untrusted text."""
    value = re.sub(r"(?i)([a-z][a-z0-9+.-]*://)[^\s/]*@", r"\1[REDACTED]@", str(value))
    value = re.sub(r"(?i)([?&](?:[^\s=&#]+)=)[^\s&#]*", r"\1[REDACTED]", value)
    value = re.sub(r"(?im)\b((?:proxy-)?authorization\s*[:=]\s*)[^\r\n]+", r"\1[REDACTED]", value)
    value = re.sub(r"(?i)\b(Bearer|Basic)\s+[A-Za-z0-9._~+/=-]+", r"\1 [REDACTED]", value)
    value = re.sub(r"(?i)\b((?:[\w.-]*(?:token|password|passwd|secret|credential|api[_-]?key)[\w.-]*)[\"']?\s*[:=]\s*)(?:\"[^\"]*\"|'[^']*'|[^\s,;]+)",
                   r"\1[REDACTED]", value)
    value = re.sub(r"\b(?:gh[pousr]_[A-Za-z0-9_]+|github_pat_[A-Za-z0-9_]+)\b", "[REDACTED]", value)
    # JSON quoting neutralizes control characters, including terminal escapes.
    escaped = json.dumps(value.strip(), ensure_ascii=True)
    return escaped if len(escaped) <= 1600 else escaped[:1580] + "...[truncated]"


def prepare(mode="update", cloud_work=False, cwd=None):
    def git(*args, allowed=(0,)):
        command = "git " + " ".join(args)
        try:
            result = subprocess.run([executable, "-C", str(root), *args], capture_output=True, text=True)
        except OSError as error:
            raise PreparationError("Could not start " + diagnostic(command) + ": " + diagnostic(error)) from None
        if result.returncode not in allowed:
            details = [name + "=" + diagnostic(value) for name, value in
                       (("stderr", result.stderr), ("stdout", result.stdout)) if value.strip()]
            raise PreparationError(diagnostic(command) + " exited " + str(result.returncode) + ": "
                                   + ("; ".join(details) or "stdout and stderr are empty"))
        return result.stdout.strip(), result.returncode

    root = Path(cwd or Path.cwd()).resolve()
    executable = resolve_git(root)
    actual = Path(git("rev-parse", "--show-toplevel")[0]).resolve()
    if actual != root or (os.name == "nt" and actual != WINDOWS_ROOT.resolve()):
        raise PreparationError("Invalid repository root; use the actual checkout root")
    if cloud_work and (os.name == "nt" or os.environ.get("MINILOOT_MAINTENANCE_HOST") != "codex-cloud"):
        raise PreparationError("--cloud-work requires explicitly authorized Codex Cloud on a non-Windows host")
    if mode not in ("update", "development"):
        raise PreparationError("Invalid mode")
    if git("status", "--porcelain=v1", "--untracked-files=all")[0]:
        raise PreparationError("Dirty worktree/index; branches were not changed")
    markers = ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply", "sequencer")
    paths = git("rev-parse", *(arg for marker in markers for arg in ("--git-path", marker)))[0].splitlines()
    if len(paths) != len(markers) or len(set(paths)) != len(markers) or any(not path.strip() for path in paths):
        raise PreparationError("Invalid Git operation marker paths")
    for marker, value in zip(markers, paths):
        path = Path(value)
        if (path if path.is_absolute() else root / path).exists():
            raise PreparationError("Unfinished Git operation")
    branch = git("symbolic-ref", "--short", "HEAD")[0]
    if branch != "new-features" and not (cloud_work and branch == "work"):
        raise PreparationError("Expected new-features, or authorized Cloud work checkout")

    def validate_remote(name, expected):
        urls = git("remote", "get-url", "--all", name)[0].splitlines()
        pushes = git("remote", "get-url", "--push", "--all", name)[0].splitlines()
        if urls != [expected] or pushes != [expected]:
            raise PreparationError(name + " URL must be exactly " + expected)

    validate_remote("origin", ORIGIN)
    if mode == "update":
        remotes = git("remote")[0].splitlines()
        if "upstream" in remotes:
            validate_remote("upstream", UPSTREAM)
        else:
            git("remote", "add", "upstream", UPSTREAM)
    origin_specs = ["+refs/heads/new-features:refs/remotes/origin/new-features"]
    if mode == "update":
        origin_specs.append("+refs/heads/master:refs/remotes/origin/master")
    git("fetch", "--no-tags", "origin", *origin_specs)
    if mode == "update":
        git("fetch", "--no-tags", "upstream", "+refs/heads/master:refs/remotes/upstream/master")

    def ancestor(left, right):
        return git("merge-base", "--is-ancestor", left, right, allowed=(0, 1))[1] == 0

    if cloud_work and branch == "work" and not ancestor("work", "origin/new-features"):
        raise PreparationError("work has unpublished/divergent history; preserved for human review")
    names = ["new-features"] + (["master"] if mode == "update" else [])
    missing = []
    for name in names:
        exists = git("show-ref", "--verify", "--quiet", "refs/heads/" + name, allowed=(0, 1))[1] == 0
        if not exists:
            missing.append(name)
        elif not ancestor(name, "origin/" + name):
            raise PreparationError(name + " has unpublished/divergent history; preserved for review")
    if mode == "update" and not ancestor("origin/master", "upstream/master"):
        raise PreparationError("origin/master is not a safe upstream-only fast-forward mirror")
    # All history gates precede branch creation, tracking changes, and checkout.
    for name in missing:
        git("branch", "--no-track", name, "refs/remotes/origin/" + name)
    for name in names:
        # --track cannot map a branch excluded by remote.origin.fetch.
        git("config", "--local", "branch." + name + ".remote", "origin")
        git("config", "--local", "branch." + name + ".merge", "refs/heads/" + name)
    if branch == "work":
        git("switch", "new-features")
    refs = ["origin/" + name for name in names]
    if mode == "update":
        refs.append("upstream/master")
    expected = ["refs/heads/" + name for name in names] + ["refs/remotes/" + ref for ref in refs]
    output = git("for-each-ref", "--format=%(refname)%09%(objectname)", *expected)[0]
    tips = {}
    for line in output.splitlines():
        fields = line.split("\t")
        if (len(fields) != 2 or fields[0] not in expected or fields[0] in tips
                or re.fullmatch(r"[0-9a-f]{40}", fields[1]) is None):
            raise PreparationError("Invalid prepared reference response")
        tips[fields[0]] = fields[1]
    if set(tips) != set(expected):
        raise PreparationError("Missing prepared references")
    return {"root": str(root), "mode": mode, "branch": "new-features",
            "created": missing, "refs": {ref: tips["refs/remotes/" + ref] for ref in refs},
            "local_tips": {name: tips["refs/heads/" + name] for name in names},
            "behind": {name: int(git("rev-list", "--count", name + "..origin/" + name)[0]) for name in names}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("update", "development"), default="update")
    parser.add_argument("--cloud-work", action="store_true")
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.mode, args.cloud_work)))
    except (PreparationError, OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
