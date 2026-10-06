---
name: miniloot-update
description: Update MiniLoot independently from upstream/master on local Windows or authorized Codex Cloud.
---

# Update MiniLoot

Follow AGENTS.md for language, identity, approvals, conflicts, delegation and failure gates. Update/atualizar authorizes Git synchronization only, never installation. Freeze the execution context once per AGENTS.md; load [cloud environment](../../references/cloud-environment.md) only for confirmed Cloud. Follow [maintenance runtime](../../references/maintenance-runtime.md): discover Python once and prepare once in update mode with the selected adapter. Reuse JSON refs; no redundant fetch/pull.

Read [initial setup](references/initial-setup.md) only for missing clone/configuration and [branch sync](references/branch-sync.md) for the common synchronization workflow, beginning with its no-op gate. Read [merge conflicts](references/merge-conflicts.md) only for actual conflicts. Windows transport fallback is routed by AGENTS.md only upon its specific failure. Never resolve conflicts or commit automatically, publish previous local commits, or create library management. Errors leave the workflow PENDENTE, never a no-op.

Report branches, incoming upstream range when present, human resolutions and publication compactly in Portuguese. Verify origin/new-features equals the approved result. Only after ALL synchronization succeeds or a complete no-op is proven, use the frozen capabilities to follow AGENTS.md's completion routing, including its exact local Windows menu and waiting for an explicit choice. Load the install skill only after valid installation authorization, never during update preparation.
