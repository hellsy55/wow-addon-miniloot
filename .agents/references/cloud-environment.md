# Cloud environment

Local Windows uses `C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot`. Codex Cloud uses the supplied actual checkout validated with git rev-parse --show-toplevel. Never use/create the Windows path or confuse a parent with the repo. Positively identify Cloud from supplied task/environment metadata; Linux or a branch called work alone is insufficient. Unknown Linux hosts do not receive special Cloud work treatment.

Git and Python 3 are required. gh is needed only for PR workflows. SVN, external libraries, PowerShell and Lua are not required for Cloud maintenance. No physical WoW installation happens in Cloud/Linux. No library management is configured; future upstream libraries/externals require human review.

Startup reads AGENTS.md and this adapter only after positive Cloud identification. Load maintenance-runtime.md only when a Python helper or prepared local checkout is needed; remote-only PR review requires neither runtime discovery nor preparation. Do not fetch/update/install or mutate branches merely to initialize the environment. After authorized safe bootstrap, work on real new-features, the intended GitHub default/development branch. master remains an independent upstream-only mirror. Do not change GitHub settings without separate authorization.

When preparation is required follow [maintenance runtime](maintenance-runtime.md), reusing the frozen environment context. Only after task/environment metadata confirms Cloud may you set `MINILOOT_MAINTENANCE_HOST=codex-cloud` and pass `--cloud-work` for isolated work. This project authorization marker is not a built-in platform variable or independent proof; Windows rejects the flag. Use update mode for full update and development mode for checkout-dependent PR work.

Cloud work must be clean and an ancestor of freshly fetched origin/new-features. Existing project branches must have no unpublished/divergent history. Update also requires origin/master to be an ancestor of upstream/master. All history gates precede branch mutation. Create missing new-features/master only from matching origin refs; configure tracking explicitly; then switch from work. Never reset/delete/merge/publish work or derive project branches from it. Tests run offline. Network/auth failures remain real pending errors: never load Windows fallback commands or physical-installation details, and never request external PowerShell or GitHub Desktop.

Minimum required network hosts: github.com for Git; api.github.com for PR metadata. Do not add repos.wowace.com, deb.debian.org, www.townlong-yak.com or other library/package hosts. No dependency installation is needed. See [official Cloud environment documentation](https://learn.chatgpt.com/docs/environments/cloud-environment).

Suggested Environment Editor startup instruction (instruction, not an automatic setup script):

```text
Read AGENTS.md in the supplied MiniLoot checkout and validate the real Git root.
This is an explicitly identified Codex Cloud environment. Do not fetch, update,
install or switch branches merely for startup. When maintenance is requested,
discover existing Python 3 once when a Python helper or prepared checkout is
needed, and follow maintenance-runtime.md. Remote-only PR review can precede
preparation. Authorize
MINILOOT_MAINTENANCE_HOST=codex-cloud only in this confirmed Cloud context.
Use safe preparation for isolated work; never reset/delete/merge/push work.
Work on real new-features after bootstrap. No Windows paths, PowerShell, WoW
installation, SVN, libraries or dependency installation. Report errors as
pending. Require complete staged review and explicit approval before commits.
```
