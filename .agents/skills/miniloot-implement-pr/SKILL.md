---
name: miniloot-implement-pr
description: Review and implement a Vladinator/wow-addon-miniloot pull request on new-features after the user's explicit implementation decision.
---

# Implement a MiniLoot PR

Follow AGENTS.md. Accept only PR URLs belonging to `Vladinator/wow-addon-miniloot`; reject other upstream repositories. Work only on new-features, never master. Stop for unexpected local changes or unfinished Git operations.

Before inspecting branch, status, or diff, or performing any staging, commit, or push, explicitly target `C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot`. Set that exact working directory for EVERY execution or use `git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" ...`. Never assume the session directory, operate in the parent directory, or rely on a `cd` from an earlier execution. First run `git rev-parse --show-toplevel` against the explicit directory and verify that it resolves to the required repository root.

If root validation or any mandatory Git check fails, STOP dependent workflow operations and report the workflow as PENDENTE. Never treat a failed branch, status, diff, ancestry, fetch, or other mandatory check as successful completion. Respect documented non-error exit codes. Do not offer installation or execute the installer from a failed Git workflow; a "not a git repository" failure must never be followed by fetch, merge, push, the installation menu, or installation.

Before applying a PR, confirm new-features and retrieve compact metadata. Show number, title, file count, additions, deletions, and all affected paths before retrieving the diff. Read full files only when the diff is insufficient. Compare with current local customizations.

Before modifying anything, explain in Portuguese what we gain, what may change, what we lose, what stays the same, and interactions with our customizations. For a small PR offer apply or ignore. For a large/complex PR offer: a) apply as-is; b) apply adapted; c) ignore a specified part; d) do not apply. Wait for the user's decision before edits. Use exactly one read-only deep_reviewer only when AGENTS.md criteria justify it. Review never grants implementation approval.

Implement only the selected scope and validate the resulting behavior. Never resolve conflicts automatically; use the update skill's conflict reference if conflicts occur. Stage only relevant files. Show the full staged file list, staged stat, and COMPLETE staged diff, then wait for explicit commit approval. Commit only after that approval, with the required English subject format and configured user identity. Push new-features only after commit and necessary publication approval; never publish unreviewed preexisting commits.

When PR implementation results in a commit, its English body must reference the PR number and source `Vladinator/wow-addon-miniloot` (for example, `Implement PR #123 from Vladinator/wow-addon-miniloot`). Do not add an AI signature. This requirement does not change the mandatory complete checkpoint and explicit approval immediately before the commit.

Verify origin/new-features contains exactly the approved result before offering installation now or stopping without installing. Choosing installation authorizes execution of the external script via the install skill without another confirmation. Report verified outcomes and any pending decisions or errors compactly in Portuguese.
