---
name: miniloot-install
description: Install MiniLoot from a fresh published origin/new-features ZIP when the user requests install MiniLoot, instalar MiniLoot, or instalar o addon.
---

# Install MiniLoot

Read [installation mechanics](references/installation-mechanics.md). The published GitHub origin/new-features ZIP is always the source; local working-tree files and uncommitted changes are never installation sources. Never publish unapproved changes just to make them available in the ZIP.

The external script is `C:\Users\jonat\Desktop\MiniLoot\atualizar-miniloot.ps1`, outside the repository. Explicitly choosing installation already authorizes execution; do not ask again. Execute in the current session:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\jonat\Desktop\MiniLoot\atualizar-miniloot.ps1"
```

Do not use Start-Process, start, or another window. If unexpected UAC occurs, tell the user manual approval is needed. Report success only after the script exits successfully; report errors and pending installation accurately.
