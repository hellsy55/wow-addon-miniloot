# Initial setup

Load only for missing clone/configuration. Reuse the frozen host/root and action eligibility from AGENTS.md, plus Python if already resolved; do not repeat environment discovery or probe installation/fallback paths. Preserve unexpected files. Setup is explicit work, not automatic startup. Windows-specific instructions below apply only on local Windows.

Local Windows: use C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot. Create the Github parent only if missing; clone https://github.com/hellsy55/wow-addon-miniloot.git only into an absent destination. Command-scoped git -c http.sslBackend=openssl clone may address documented Schannel errors. Once cloned, use/validate repository-local http.sslBackend=openssl only when needed; never change global SSL configuration or disable sslVerify. Preserve the external installer C:\Users\jonat\Desktop\MiniLoot\atualizar-miniloot.ps1; never execute it during setup.

For confirmed Cloud, use the already loaded [Cloud adapter](../../../references/cloud-environment.md); missing/invalid supplied checkout is a real pending error. Do not load this reference for routine Cloud preparation.

Follow [maintenance runtime](../../../references/maintenance-runtime.md), reusing an existing runtime and successful preparation rather than repeating them. Origin must exactly match https://github.com/hellsy55/wow-addon-miniloot.git. Update alone may add missing upstream https://github.com/Vladinator/wow-addon-miniloot.git. Reject incorrect URLs. Missing local branches derive only from their refreshed matching origin refs. Finish on new-features with tracking; master remains upstream-only. Do not change remote.origin.fetch or GitHub default-branch settings.

No Lua/TOC/pkgmeta changes, libraries, integration, commit, push, or installation during infrastructure setup.
