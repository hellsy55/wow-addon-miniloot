# Initial setup

Distinguish local Windows from positively identified Codex Cloud using AGENTS.md and the environment reference. Preserve unexpected files. Setup is explicit work, not automatic startup.

Local Windows: use C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot. Create the Github parent only if missing; clone https://github.com/hellsy55/wow-addon-miniloot.git only into an absent destination. Command-scoped git -c http.sslBackend=openssl clone may address documented Schannel errors. Once cloned, use/validate repository-local http.sslBackend=openssl only when needed; never change global SSL configuration or disable sslVerify. Preserve the external installer C:\Users\jonat\Desktop\MiniLoot\atualizar-miniloot.ps1; never execute it during setup.

Cloud: use the checkout supplied by the environment. Never clone to C:\, create Windows paths, create a PowerShell installer, or execute physical installation. Missing/invalid checkout is a real pending error.

Follow maintenance-runtime.md: discover Python once and prepare once in the requested mode. Origin must exactly match https://github.com/hellsy55/wow-addon-miniloot.git. Update alone may add missing upstream https://github.com/Vladinator/wow-addon-miniloot.git. Reject incorrect URLs. Missing local branches derive only from their refreshed matching origin refs. Authorized Cloud work follows every clean/history gate before switching; never derive project branches from work. Finish on new-features with tracking; master remains upstream-only. Do not change remote.origin.fetch or GitHub default-branch settings.

No Lua/TOC/pkgmeta changes, libraries, integration, commit, push, or installation during infrastructure setup.
