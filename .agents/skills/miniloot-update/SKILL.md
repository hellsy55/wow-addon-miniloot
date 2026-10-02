---
name: miniloot-update
description: Update MiniLoot from upstream/master while independently synchronizing new-features and master; handles update and atualizar commands.
---

# Update MiniLoot

Follow repository AGENTS.md for branch invariants, approvals, language, delegation, and error handling.
For a missing clone or initial configuration, read [initial setup](references/initial-setup.md). For normal updates, read [branch sync](references/branch-sync.md). Read [merge conflicts](references/merge-conflicts.md) only when conflicts occur.

Check current branch and working tree once; stop for unexpected local changes. Fetch origin and upstream once each and reuse their remote-tracking refs. Avoid unnecessary pull, repeated status, checkout, merge, push, and semantic analysis. Never automatically commit or resolve conflicts.

Report new-features, master, incoming upstream commits when present, conflicts and adopted resolutions when present, push, and installation if performed. A fully current repository needs only a compact no-op report.
