# MiniLoot workspace rules

Speak to the user in Portuguese. Write project files, documentation, code comments, and Git messages in English. Use only the configured user Git identity. Do not add AI signatures, generated-by notices, or Co-authored-by trailers.

- Do not pin models or reasoning effort in this repository. The main agent and its subagents must respect the session/task selections and inherit them when supported by Codex.

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

At workflow entry, resolve and freeze only host (`local_windows`, positively identified `cloud`, or another host) and validated repository root. Record environment-specific action eligibility from that host, not probed capability: physical installation and the specific HTTPS fallback are potentially eligible only on local Windows. Do not discover Python, inspect installer/AddOns paths, or perform fallback-specific checks at entry. Add and freeze Python only before the first Python helper or prepared-local-checkout stage; reuse the same runtime and successful preparation afterward. Reuse this context through all stages and an authorized installation handoff. Rediscover facts only for concrete invalidation, such as a changed checkout/session/runtime or contradictory evidence; refresh Git facts affected by mutations without rediscovering the environment. Explicit Git targeting on EVERY execution remains mandatory. The preparation helper's own root validation is an independent safety gate, not a reason to repeat agent preflight.

On positively identified Codex Cloud, use the actual checkout root returned by `git rev-parse --show-toplevel`, explicitly targeted on every execution. Never use or create the Windows path there. Confirm supplied task/environment metadata; Linux or a branch named work alone is not Cloud evidence. Load `.agents/references/cloud-environment.md` only for confirmed Cloud. Its safe bootstrap is the only treatment for isolated Cloud work; never reset, delete, merge, publish, or derive project branches from work. On other non-Windows hosts, use a validated actual root but do not enable Cloud work treatment. For update/PR preparation, load `.agents/references/maintenance-runtime.md`; do not run preparation merely for startup or installation.

Before any Git workflow, run `git rev-parse --show-toplevel` against the environment-specific explicit directory and verify that it resolves to the required repository root. This invariant applies to update and implement PR, including branch detection, status, diff, staging, commit, and push. Never operate in the parent directory.

If this preflight fails (including "not a git repository") or returns another root, STOP the workflow. Any failed mandatory Git check, including status, branch detection, ancestry, fetch, or comparison, leaves the update PENDING, never completed or a no-op. Respect documented non-error exit codes such as ancestry exit 1. Do not continue dependent fetch, merge, or push operations after a failure. Do not show the installation menu or execute installation from a failed Git workflow. Git failures outside the repository followed by installer execution are explicitly forbidden.

The update installation menu is reachable ONLY after ALL required Git synchronization succeeds, or a REAL no-op is proven by all required Git comparisons. On failure, report the update as PENDENTE in Portuguese without offering installation. The separate direct-install authorization exception above remains unchanged.

Attempt authorized HTTPS fetch/push normally inside Codex using normal Git validations; fallback eligibility adds no preventive checks. ONLY after the observed Codex HTTPS transport failure (`git-remote-https.exe` crash, exit 128 with empty stdout/stderr, or an equivalent transport failure) occurs on local Windows, load `.agents/skills/miniloot-update/references/windows-https-fallback.md` and perform its specific checks, including repository-local `http.sslBackend=openssl` validation before external execution. Reuse the validated root. Preserve state, report PENDENTE, and mark transport unavailable for the REST of this execution: no further internal HTTPS fetch/push, including verification. Failed fallback checks remain pending; ordinary network/auth errors do not enable this fallback. Never disable `sslVerify`, change credential helpers or global Git configuration, generate tokens, or automatically switch to SSH.

Non-Windows hosts never load the Windows HTTPS fallback or physical-installation details, execute PowerShell/physical WoW installation, or offer the installation menu. Network/auth failures remain PENDENTE. After successful verified publication, state that installation is a local Windows step. Only after a valid installation choice or unequivocal direct installation request, use the frozen host eligibility to reject non-Windows installation before loading its skill/details. On local Windows load the install skill and verify installer/AddOns paths only at that authorized installation stage, never during update or PR review.

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

Locate files with `rg --files` and symbols with `rg -n` before reading whole files; read relevant excerpts first and expand context only as needed, without truncating required complete review diffs.
Treat failed commands as real errors; stop the affected stage and report it pending. Preserve unexpected files and never delete outside the project's explicitly owned structures. Never resolve merge conflicts automatically; follow the update conflict reference and wait for a user choice.
Do routine work in the primary agent. Do not delegate status, fetch, fast-forward, simple updates, no-ops, installation, small diffs, or small clear PRs. Use exactly one read-only `deep_reviewer` only when it materially improves an important decision: nontrivial conflicts, large or ambiguous PRs, potential customization loss, interdependent modules, difficult regressions, or genuinely uncertain semantic interactions. Its review never authorizes edits, conflict resolution, commits, pushes, or installation.

Do not create AlterEgo library management: no `miniloot-libs`, `alterego-libs`, `scripts/check_lib_updates.py`, `.pkgmeta-lock.json`, `.pkgmeta-cache`, `check libs`, or `update with libs`. No externals or vendored Libs exist. Do not add lockfiles, caches, library update scripts, SVN setup, or any equivalent library management. If upstream later introduces libraries/externals, STOP and report for human review; never invent a workflow automatically.

Report verified results compactly in Portuguese, aggregating healthy Git output. Explicitly state pending errors, choices, or conflicts. After a completed update (including a no-op) or approved PR publication, verify origin/new-features contains exactly the approved result, then on local Windows present the exact installation menu above and STOP waiting for an explicit choice. Choosing installation authorizes execution without another confirmation.

## Token Savings Reporting

- At the start of each Codex Cloud session, verify RTK availability and version at the first point allowed by the workflow. After mandatory identification and preflight checkpoints, and any applicable workflow menu, capture a baseline for each task using the installed version's supported `rtk gain` format before eligible work begins, when available and compatible with task restrictions. Use only telemetry formats, options, and schemas supported by the installed RTK version. Do not assume that unsupported flags or telemetry fields exist. Normal local RTK tracking operations, including creation or updates of its tracking database outside the checkout, are permitted when compatible with task restrictions. Do not interpret repository preservation requirements alone as a prohibition of normal RTK tracking. Explicit user restrictions on writes remain binding. Do not create a tracking database solely to report savings for a read-only task.
- Default to an explicit RTK prefix for every supported command whose filtered output preserves the required information. Use it for the first genuinely eligible exploratory command after the applicable checkpoints and throughout the workflow, including exploratory searches, directory listings, symbol navigation, and noncritical inspections. Consult RTK help when support is unclear. Do not assume native commands are intercepted.
- Confirm the current `AGENTS.md` after preparing an updated checkout and at relevant stage or branch transitions. If the applicable instructions have changed, reread them before continuing. Reapply the RTK policy after checkpoints, context resumptions, checkout preparation, and branch transitions.
- Use native commands for exact, complete, unfiltered, or machine-readable output. Keep critical Git operations native, including refs, ancestry, conflict evidence, index verification, complete diffs, and publication. Keep artifact integrity checks native. These exceptions do not extend to eligible exploration.
- Fall back to native execution if filtering is insufficient, ambiguous, or truncated, or if RTK is unavailable or malfunctioning. Report the limitation and retain a concise justification for otherwise eligible native reads when relevant. After any command with side effects, inspect the resulting state before deciding whether a retry is safe.
- Capture counters again at applicable task boundaries, subject to the same restrictions. At task completion, capture the final supported counters and calculate the attributable difference against the initial baseline whenever reliable measurements are available. Separate stage results from cumulative task results without double counting. Never invent percentages, totals, command counts, or savings estimates. Do not present global or historical savings as attributable to the current task without reliable task-specific evidence.
- Append a compact `Token Savings` section in Portuguese to the final report for every repository workflow, including updates, PR implementation, temporary testing, maintenance, and no-ops. Distinguish zero optimized invocations, measured zero savings, unavailable metrics, and unavailable RTK. If metrics are unreliable, report `Token savings: unavailable` and the reason.
- When attributable, report the command count, filtered reads with and without reduction, passthrough, and estimated terminal-output tokens before and after filtering, absolute savings, and reduction percentage with their baseline and scope. RTK estimates concern terminal output. Report any available actual task usage separately from those estimates and from billed usage. Other optimizations may be noted qualitatively without invented savings. Claim an exact unoptimized comparison only when an equivalent baseline was measured.
- Avoid redundant commands, unoptimized reruns, tooling installs, workflow changes, and expensive measurements for reporting alone. Never prioritize savings or telemetry over correctness, mandatory validation, repository or artifact integrity, approvals, or delivery. Do not let metric collection delay or block development, testing, approval checkpoints, or authorized ZIP and Google Drive delivery. Keep reporting concise.
