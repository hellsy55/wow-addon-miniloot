# Cloud update delivery

Load this reference only when a Cloud prompt explicitly requests it after the
user selects a workflow that actually performs an update. It adds delivery rules;
it never replaces, changes, or bypasses [AGENTS.md](../../AGENTS.md) or the
[update skill](../skills/miniloot-update/SKILL.md). Read it before the first
modification of the installable target to capture the initial state.

Checkpoints, conflicts, approvals, merge semantics, libraries, publication, and
installation remain governed exclusively by the normal project workflow. If that
workflow pauses for approval or a decision, or fails, the update remains pending:
do not generate final delivery artifacts early. Options that do not perform an
update do not automatically receive an installer or update summary.

## Initial installable state

- Determine the installable branch/state from AGENTS.md: for MiniLoot, use
  `new-features`. Compare only this fork's initial and final installable states.
- Before its first modification, record the full SHA, short SHA, commit subject,
  and addon version when it can be determined reliably. Preserve that state as
  the immutable delivery base throughout the workflow.
- Record auxiliary/mirror branches if the workflow needs them; they never replace
  the installable base.

## Incremental installer

Only after the normal workflow is genuinely complete:

- Compute the net difference from the recorded initial installable state to the
  final installable state. Use only final file contents; include necessary new
  files and exclude files that end identical to the base or remain unchanged.
- Include only files belonging to the installed addon. Exclude temporary files,
  tests, operational scripts/helpers, Codex/Cloud tooling, operational
  documentation, and packaging artifacts outside the installed addon.
- Generate exactly one incremental installer, never a full distribution. Do not
  include entire modules/addons merely to complete a distribution.
- Map repository-root files into `MiniLoot/`, for example `MiniLoot.lua` to
  `MiniLoot/MiniLoot.lua` and `Modules/Example.lua` to
  `MiniLoot/Modules/Example.lua`. Add no outer wrapper directory.
- Do not create or include any library management system; follow the project's
  existing library boundary in AGENTS.md.
- End the ZIP name with `_installer.zip`; prefer a reliable final addon version,
  otherwise use the final short SHA.
- A ZIP cannot represent deletions: list required manual removal paths separately
  in Portuguese. Never install, extract, or copy the ZIP into the WoW directory.

## Update summary

For the installer, produce a concise English summary of the complete net
functional difference between the initial base and final state, not merely the
last commit. Include relevant final runtime code, behavior, UI, content, data,
functional configuration, and compatibility changes without omitting material
functional changes. Mention libraries only if their distributed runtime content
actually changed, subject to the project's library boundary.

Exclude reverted intermediate changes, workflow/process details, merges as a
process, checkpoints, debugging, intermediate conflicts, and discarded attempts.
Exclude AGENTS.md, agent tools, Codex/Cloud tooling, environment maintenance,
auxiliary scripts, bootstrap, proxies, checkout preparation, operational
documentation, tests, CI/CD, checkers, drift baselines, locks, and infrastructure
metadata. For mixed commits retain the functional portion: filter by the effective
final change, never by commit title alone.

Show only final functional addon changes in a single copy-ready code block, using
`Module (type): item; item. Module2 (type): item`. Group the same module/type with
`; `, separate different groups with `. `, and omit a trailing period.

## Final report

For the target/installer, report in Portuguese:

- Target when applicable, initial version if available, initial subject and short
  SHA, final version if available, and final subject and short SHA.
- The `initial -> final` transition, ZIP filename, and number of packaged files.
- Required manual deletions, or explicitly none.
- Confirmation that the ZIP contains only the final net difference and that no
  files were installed in the WoW directory.
