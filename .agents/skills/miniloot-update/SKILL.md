---
name: miniloot-update
description: Update MiniLoot from upstream/master while independently synchronizing new-features and master; handles update and atualizar commands.
---

# Update MiniLoot

Follow repository AGENTS.md for branch invariants, approvals, language, delegation, and error handling.
`update`, `atualizar`, `update MiniLoot`, and equivalent requests authorize ONLY Git synchronization. They NEVER authorize installation automatically. Update completion, a no-op, an updated origin/new-features, completed commits/pushes, and remote ZIP availability do not authorize installation.
For a missing clone or initial configuration, read [initial setup](references/initial-setup.md). For normal updates, read [branch sync](references/branch-sync.md). Read [merge conflicts](references/merge-conflicts.md) only when conflicts occur.

Before any Git workflow, explicitly target `C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot` and confirm `git rev-parse --show-toplevel` resolves to that root. Set this working directory for EVERY execution, or use `git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" ...`. Never assume the session directory or rely on an earlier `cd`.

If the root preflight or any mandatory Git check fails, STOP dependent operations and report the update as PENDENTE. Status, branch detection, ancestry, fetch, and comparison failures never mean completion or no-op; respect documented non-error exit codes. Do not proceed to fetch, merge, push, the installation menu, or installation after a failed preflight. The menu below is permitted ONLY after all required synchronization succeeds or all required comparisons prove a real no-op. Never run the installer after Git commands fail outside the repository.

Check current branch and working tree once; stop for unexpected local changes. Fetch origin and upstream once each and reuse their remote-tracking refs. Avoid unnecessary pull, repeated status, checkout, merge, push, and semantic analysis. Never automatically commit or resolve conflicts.

Report new-features, master, incoming upstream commits when present, conflicts and adopted resolutions when present, and push. A fully current repository needs a compact no-op report followed by the same mandatory installation checkpoint as any successful synchronization:

```text
a) instalar MiniLoot agora
b) parar sem instalar
```

ALWAYS show this menu in Portuguese and STOP waiting for the user's response. Only an explicit choice to install authorizes loading the install skill and executing its command. An unequivocal direct installation request is handled by the install skill and does not require this menu.
