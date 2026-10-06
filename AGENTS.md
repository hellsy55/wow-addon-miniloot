# MiniLoot workspace rules

Speak to the user in Portuguese. Write project files, documentation, code comments, and Git messages in English. Use only the configured user Git identity. Do not add AI signatures, generated-by notices, or Co-authored-by trailers.

## Routing

Recognize case-insensitive commands and close wording variants:
- `update`, `atualizar`, `update MiniLoot`, `atualizar MiniLoot`: read `.agents/skills/miniloot-update/SKILL.md`.
- `install MiniLoot`, `instalar MiniLoot`, `instalar o addon`: read `.agents/skills/miniloot-install/SKILL.md`.
- `implement PR <URL>`, `implementar PR <URL>`: read `.agents/skills/miniloot-implement-pr/SKILL.md`.

Update commands and their equivalents authorize ONLY the Git synchronization workflow, never installation. After successful synchronization, including a complete no-op, on local Windows ALWAYS present this exact Portuguese menu and STOP waiting for the user's response:

```text
a) instalar MiniLoot agora
b) parar sem instalar
```

Only an explicit response choosing installation authorizes running `powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\jonat\Desktop\MiniLoot\atualizar-miniloot.ps1"`. Never infer installation authorization from update completion, a no-op, an updated origin/new-features, a completed commit/push, or remote ZIP availability. A direct, unequivocal installation request such as `install MiniLoot`, `instalar MiniLoot`, or `instalar o addon` is the sole exception: it authorizes installation without the menu.

## Repository root and Git failure gate

On local Windows, ALL project Git operations must explicitly target `C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot`. Never assume the Codex session's current working directory is the repository. For EVERY execution, either set that exact working directory or use `git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" ...`. Never rely on a `cd` from an earlier execution.

On positively identified Codex Cloud, use the actual checkout root returned by `git rev-parse --show-toplevel`, explicitly targeted on every execution. Never use or create the Windows path there. Linux or a branch named work alone is not Cloud evidence. Read `.agents/references/cloud-environment.md` and `.agents/references/maintenance-runtime.md`. An isolated Cloud work checkout may only use the documented safe bootstrap; never reset, delete, merge, publish, or derive project branches from work. On other non-Windows hosts, use a validated actual root but do not enable Cloud work treatment.

Before any Git workflow, run `git rev-parse --show-toplevel` against the environment-specific explicit directory and verify that it resolves to the required repository root. This invariant applies to update and implement PR, including branch detection, status, diff, staging, commit, and push. Never operate in the parent directory.

If this preflight fails (including "not a git repository") or returns another root, STOP the workflow. Any failed mandatory Git check, including status, branch detection, ancestry, fetch, or comparison, leaves the update PENDING, never completed or a no-op. Respect documented non-error exit codes such as ancestry exit 1. Do not continue dependent fetch, merge, or push operations after a failure. Do not show the installation menu or execute installation from a failed Git workflow. Git failures outside the repository followed by installer execution are explicitly forbidden.

The update installation menu is reachable ONLY after ALL required Git synchronization succeeds, or a REAL no-op is proven by all required Git comparisons. On failure, report the update as PENDENTE in Portuguese without offering installation. The separate direct-install authorization exception above remains unchanged.

Attempt authorized HTTPS fetch/push normally inside Codex; handle failures with useful diagnostics as their actual errors. ONLY on local Windows, if, after repository-root and local `http.sslBackend=openssl` validation, the operation instead exhibits the observed Codex HTTPS transport failure (`git-remote-https.exe` crash, exit 128 with empty stdout/stderr, or an equivalent transport failure), treat Codex HTTPS transport as unavailable for the REST of that workflow execution: no further HTTPS fetch/push inside Codex, including verification. Never retry in a loop, disable `sslVerify`, change `credential.helper` or global Git configuration, generate a token, or automatically switch to SSH. Preserve all local state and report remote synchronization/publication as PENDENTE. Give the exact failed Git operation with the explicit `git -C` repository path for normal PowerShell outside Codex, then STOP waiting for confirmation. After an external fetch, verify only with local read-only comparisons of the updated remote-tracking refs. After an external push, first check the corresponding local remote-tracking ref against the approved result; if insufficient, request the exact external fetch, wait for confirmation, and verify locally. GitHub Desktop is an option for origin push/fetch only when the equivalent operation is available in its interface; use the supplied PowerShell command for operations not clearly exposed, such as a specific upstream fetch. Never assume Desktop performed a different operation from the one confirmed. Confirmation without sufficient local Git evidence is not proof: remain PENDENTE without dependent integration, installation menu, or installation until verified. See the exact fallback commands in `.agents/skills/miniloot-update/references/branch-sync.md`.

On Cloud, fetch/push/auth/network failures remain real errors and leave the workflow PENDENTE. Never request external PowerShell or GitHub Desktop as Cloud fallback. Do not disable sslVerify, change global credential helpers, create tokens, or automatically switch to SSH. Cloud/Linux never executes PowerShell or physical WoW installation and never offers the installation menu; after successful verified publication, state that installation is a local Windows step.

## Branch invariants

Origin: https://github.com/hellsy55/wow-addon-miniloot.git
Upstream: https://github.com/Vladinator/wow-addon-miniloot.git
`new-features` is the intended GitHub default/development branch; do not change GitHub settings without separate authorization. Use the existing `new-features` branch tracking `origin/new-features` for development, customizations, Codex infrastructure, PR implementation, and published installation content. Keep `master` free of fork-specific customizations.
Synchronize both branches independently from `upstream/master`. Never integrate master into new-features or new-features into master. Master advances only by fast-forward; never create a merge commit there. Finish on new-features.

## Commit and publication checkpoint

Implementation authorization never authorizes a commit. Before EVERY commit, including a merge commit:
1. Inspect all staged files and unstage unrelated files without discarding their contents.
2. Show `git diff --cached --name-only`, `git diff --cached --name-status`, `git diff --cached --stat`, and the COMPLETE `git diff --cached`, without size exceptions.
3. Wait for explicit user approval immediately before executing `git commit`; any subsequent staged change requires a new complete checkpoint and approval.

Never commit automatically. Never publish preexisting local commits without reviewing them and receiving explicit publication authorization. Obtain all required approvals before pushing.
Commit subjects must be a single imperative line in English: `Module (type): change`. Group same-module/type changes with `; `, separate distinct groups with `. `, and omit a trailing period. Example: `MiniLoot (fix): fix group loot rolls. Workflow (chore): update installation logic`.
Never commit local test, scratch, diagnostic, temporary, or other development-only artifacts unless the user explicitly requests their inclusion.

## Operational boundaries

Treat failed commands as real errors; stop the affected stage and report it pending. Preserve unexpected files and never delete outside the project's explicitly owned structures. Never resolve merge conflicts automatically; follow the update conflict reference and wait for a user choice.
Do routine work in the primary agent. Do not delegate status, fetch, fast-forward, simple updates, no-ops, installation, small diffs, or small clear PRs. Use exactly one read-only `deep_reviewer` only when it materially improves an important decision: nontrivial conflicts, large or ambiguous PRs, potential customization loss, interdependent modules, difficult regressions, or genuinely uncertain semantic interactions. Its review never authorizes edits, conflict resolution, commits, pushes, or installation.

Do not create AlterEgo library management: no `miniloot-libs`, `alterego-libs`, `scripts/check_lib_updates.py`, `.pkgmeta-lock.json`, `.pkgmeta-cache`, `check libs`, or `update with libs`. No externals or vendored Libs exist. Do not add lockfiles, caches, library update scripts, SVN setup, or any equivalent library management. If upstream later introduces libraries/externals, STOP and report for human review; never invent a workflow automatically.

Report verified results compactly in Portuguese, aggregating healthy Git output. Explicitly state pending errors, choices, or conflicts. After a completed update (including a no-op) or approved PR publication, verify origin/new-features contains exactly the approved result, then on local Windows present the exact installation menu above and STOP waiting for an explicit choice. Choosing installation authorizes execution without another confirmation.
