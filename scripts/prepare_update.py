"""Prepare maintenance refs and branches; never integrate or publish content."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ORIGIN = "https://github.com/hellsy55/wow-addon-miniloot.git"
UPSTREAM = "https://github.com/Vladinator/wow-addon-miniloot.git"
WINDOWS_ROOT = Path(r"C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot")


class PreparationError(RuntimeError):
    pass


def prepare(mode="update", cloud_work=False, cwd=None):
    def git(*args, allowed=(0,)):
        result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
        if result.returncode not in allowed:
            raise PreparationError("git " + " ".join(args) + ": " + result.stderr.strip())
        return result.stdout.strip(), result.returncode

    root = Path(cwd or Path.cwd()).resolve()
    actual = Path(git("rev-parse", "--show-toplevel")[0]).resolve()
    if actual != root or (os.name == "nt" and actual != WINDOWS_ROOT.resolve()):
        raise PreparationError("Invalid repository root; use the actual checkout root")
    if cloud_work and (os.name == "nt" or os.environ.get("MINILOOT_MAINTENANCE_HOST") != "codex-cloud"):
        raise PreparationError("--cloud-work requires explicitly authorized Codex Cloud on a non-Windows host")
    if mode not in ("update", "development"):
        raise PreparationError("Invalid mode")
    if git("status", "--porcelain=v1", "--untracked-files=all")[0]:
        raise PreparationError("Dirty worktree/index; branches were not changed")
    for marker in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply", "sequencer"):
        path = Path(git("rev-parse", "--git-path", marker)[0])
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
    remotes = git("remote")[0].splitlines()
    if mode == "update":
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
    return {"root": str(root), "mode": mode, "branch": "new-features",
            "created": missing, "refs": {ref: git("rev-parse", ref)[0] for ref in refs},
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
