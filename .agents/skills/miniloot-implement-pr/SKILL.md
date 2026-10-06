---
name: miniloot-implement-pr
description: Review and implement a Vladinator/wow-addon-miniloot pull request on new-features after the user's explicit implementation decision.
---

# Implement a MiniLoot PR

Follow AGENTS.md. Accept only PR URLs belonging to `Vladinator/wow-addon-miniloot`; reject other upstream repositories. Work only on new-features, never master. Stop for unexpected local changes or unfinished Git operations.

Resolve and explicitly target the environment-specific repository root per AGENTS.md; never operate in its parent. Read [maintenance runtime](../../references/maintenance-runtime.md) and [cloud environment](../../references/cloud-environment.md). Run runtime discovery once and preparation once with `--mode development`; add `--cloud-work` ONLY for an explicitly authorized Codex Cloud work checkout. Reuse the resulting refs; do not fetch repeatedly. The helper must succeed and the real current branch must be new-features before PR analysis, application, staging, or commit. Local Windows retains its canonical path and normal new-features workflow. Never touch master/upstream unnecessarily in development preparation.

After successful preparation, use the returned `behind["new-features"]` count on both local Windows and Cloud. If it is greater than zero, run ONLY `git merge --ff-only origin/new-features` before any PR analysis or application. Do not fetch again. Then prove local new-features == origin/new-features by comparing successful `git rev-parse new-features` and `git rev-parse origin/new-features` results, including when behind is zero. A failed fast-forward, failed comparison, or unequal tips stops the workflow as PENDENTE. Ahead/divergent history remains blocked by the helper for human review; never reset, overwrite, or rewrite local commits. The helper itself continues to preserve existing local branches and never performs this fast-forward.

If root validation or any mandatory Git check fails, STOP dependent workflow operations and report the workflow as PENDENTE. Never treat a failed branch, status, diff, ancestry, fetch, or other mandatory check as successful completion. Respect documented non-error exit codes. Do not offer installation or execute the installer from a failed Git workflow; a "not a git repository" failure must never be followed by fetch, merge, push, the installation menu, or installation.

Before applying a PR, confirm new-features and retrieve compact metadata. Show number, title, file count, additions, deletions, and all affected paths before retrieving the diff. Read full files only when the diff is insufficient. Compare with current local customizations.

Before modifying anything, explain in Portuguese what we gain, what may change, what we lose, what stays the same, and interactions with our customizations. For a small PR offer apply or ignore. For a large/complex PR offer: a) apply as-is; b) apply adapted; c) ignore a specified part; d) do not apply. Wait for the user's decision before edits. Use exactly one read-only deep_reviewer only when AGENTS.md criteria justify it. Review never grants implementation approval.

Implement only the selected scope and validate the resulting behavior. Never resolve conflicts automatically; use the update skill's conflict reference if conflicts occur. Stage only relevant files. Show staged name-only, name-status, staged stat, and COMPLETE staged diff, then wait for explicit commit approval. Commit only after that approval, with the required English subject format and configured user identity. Push new-features only after commit and necessary publication approval; never publish unreviewed preexisting commits.

When PR implementation results in a commit, its English body must reference the PR number and source `Vladinator/wow-addon-miniloot` (for example, `Implement PR #123 from Vladinator/wow-addon-miniloot`). Do not add an AI signature. This requirement does not change the mandatory complete checkpoint and explicit approval immediately before the commit.

Verify origin/new-features contains exactly the approved result before the local Windows installation menu and wait. On Cloud/Linux, only state that physical installation is a local Windows step; do not offer a menu or execute PowerShell. Choosing installation authorizes execution of the external script via the install skill without another confirmation. Report verified outcomes and any pending decisions or errors compactly in Portuguese.
