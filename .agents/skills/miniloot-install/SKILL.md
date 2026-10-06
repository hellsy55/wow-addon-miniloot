---
name: miniloot-install
description: Install MiniLoot from a fresh published origin/new-features ZIP when the user requests install MiniLoot, instalar MiniLoot, or instalar o addon.
---

# Install MiniLoot

First identify the host using [cloud environment](../../references/cloud-environment.md). Cloud/Linux: do not execute PowerShell or offer any installation menu, even for a direct install request. Inform the user in Portuguese that physical installation is a local Windows step and stop. All execution and menu instructions below apply ONLY to local Windows.

Installation requires separate, explicit authorization: either an explicit response choosing `a) instalar MiniLoot agora` after the update menu, or an unequivocal direct request such as `install MiniLoot`, `instalar MiniLoot`, or `instalar o addon`. A direct installation request authorizes execution without showing the menu first.

`update`, `atualizar`, `update MiniLoot`, and equivalent requests authorize ONLY Git synchronization, NEVER installation. Do not execute the installer based on update completion, a no-op, an updated origin/new-features, a completed commit/push, or remote ZIP availability. After successful synchronization, including a no-op, ALWAYS present in Portuguese:

```text
a) instalar MiniLoot agora
b) parar sem instalar
```

STOP waiting for the user's response. Option b ends the workflow without installation; only an explicit installation choice authorizes the command below.

Read [installation mechanics](references/installation-mechanics.md). The published GitHub origin/new-features ZIP is always the source; local working-tree files and uncommitted changes are never installation sources. Never publish unapproved changes just to make them available in the ZIP.

The external script is `C:\Users\jonat\Desktop\MiniLoot\atualizar-miniloot.ps1`, outside the repository. Explicitly choosing installation already authorizes execution; do not ask again. Execute in the current session:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\jonat\Desktop\MiniLoot\atualizar-miniloot.ps1"
```

Do not use Start-Process, start, or another window. If unexpected UAC occurs, tell the user manual approval is needed. Report success only after the script exits successfully; report errors and pending installation accurately.
