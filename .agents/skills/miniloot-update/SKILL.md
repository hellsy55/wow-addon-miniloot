---
name: miniloot-update
description: Update MiniLoot independently from upstream/master on local Windows or authorized Codex Cloud.
---

# Update MiniLoot

Follow AGENTS.md for language, identity, approvals, conflicts, delegation and failure gates. Update/atualizar authorizes Git synchronization only, never installation. Resolve host/root using [cloud environment](../../references/cloud-environment.md). Follow [maintenance runtime](../../references/maintenance-runtime.md): discover Python once, prepare once in update mode, adding --cloud-work only for an explicitly authorized Cloud work checkout. Reuse JSON refs; no redundant fetch/pull.

Read [initial setup](references/initial-setup.md) for missing clone/configuration and [branch sync](references/branch-sync.md) for updates. Read [merge conflicts](references/merge-conflicts.md) only when needed. Never resolve conflicts or commit automatically, publish previous local commits, or create library management. Errors leave the workflow PENDENTE, never a no-op.

Report branches, incoming upstream range when present, human resolutions and publication compactly in Portuguese. Verify origin/new-features equals the approved result. Cloud/Linux: only state that physical installation is a local Windows step; no menu or PowerShell. Local Windows: after ALL synchronization succeeds or a complete no-op is proven, show exactly and wait:

```text
a) instalar MiniLoot agora
b) parar sem instalar
```

Only choice a authorizes installation through the install skill. An unequivocal direct install request follows that skill's Windows-only exception.
