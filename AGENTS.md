# MiniLoot workspace rules

Speak to the user in Portuguese. Write project files, documentation, code comments, and Git messages in English. Use only the configured user Git identity. Do not add AI signatures, generated-by notices, or Co-authored-by trailers.

## Routing

Recognize case-insensitive commands and close wording variants:
- `update`, `atualizar`, `update MiniLoot`, `atualizar MiniLoot`: read `.agents/skills/miniloot-update/SKILL.md`.
- `install MiniLoot`, `instalar MiniLoot`, `instalar o addon`: read `.agents/skills/miniloot-install/SKILL.md`.
- `implement PR <URL>`, `implementar PR <URL>`: read `.agents/skills/miniloot-implement-pr/SKILL.md`.

## Branch invariants

Origin: https://github.com/hellsy55/wow-addon-miniloot.git
Upstream: https://github.com/Vladinator/wow-addon-miniloot.git
Use the existing `new-features` branch tracking `origin/new-features` for development, customizations, Codex infrastructure, PR implementation, and published installation content. Keep `master` free of fork-specific customizations.
Synchronize both branches independently from `upstream/master`. Never integrate master into new-features or new-features into master. Master advances only by fast-forward; never create a merge commit there. Finish on new-features.

## Commit and publication checkpoint

Implementation authorization never authorizes a commit. Before EVERY commit, including a merge commit:
1. Inspect all staged files and unstage unrelated files without discarding their contents.
2. Show the complete staged file list, `git diff --cached --stat`, and the COMPLETE `git diff --cached`.
3. Wait for explicit user approval immediately before executing `git commit`; any subsequent staged change requires a new complete checkpoint and approval.

Never commit automatically. Never publish preexisting local commits without reviewing them and receiving explicit publication authorization. Obtain all required approvals before pushing.
Commit subjects must be a single imperative line in English: `Module (type): change`. Group same-module/type changes with `; `, separate distinct groups with `. `, and omit a trailing period. Example: `MiniLoot (fix): fix group loot rolls. Workflow (chore): update installation logic`.
Never commit local test, scratch, diagnostic, temporary, or other development-only artifacts unless the user explicitly requests their inclusion.

## Operational boundaries

Treat failed commands as real errors; stop the affected stage and report it pending. Preserve unexpected files and never delete outside the project's explicitly owned structures. Never resolve merge conflicts automatically; follow the update conflict reference and wait for a user choice.
Do routine work in the primary agent. Do not delegate status, fetch, fast-forward, simple updates, no-ops, installation, small diffs, or small clear PRs. Use exactly one read-only `deep_reviewer` only when it materially improves an important decision: nontrivial conflicts, large or ambiguous PRs, potential customization loss, interdependent modules, difficult regressions, or genuinely uncertain semantic interactions. Its review never authorizes edits, conflict resolution, commits, pushes, or installation.

Do not create AlterEgo library management: no `miniloot-libs`, `alterego-libs`, `scripts/check_lib_updates.py`, `.pkgmeta-lock.json`, `.pkgmeta-cache`, `check libs`, or `update with libs`. The existing `.pkgmeta` does not imply a vendored-library workflow.

Report verified results compactly in Portuguese, aggregating healthy Git output. Explicitly state pending errors, choices, or conflicts. After a completed, approved update or PR publication, verify origin/new-features contains exactly the approved result before offering installation now or stopping without installation. Choosing installation authorizes execution without another confirmation.
