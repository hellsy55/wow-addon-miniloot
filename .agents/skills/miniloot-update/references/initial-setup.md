# Initial setup

Repository: `C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot`.
Preserve unexpected files. Create the Github parent only if missing; clone the fork only into an absent destination. Set origin to `https://github.com/hellsy55/wow-addon-miniloot.git` and upstream to `https://github.com/Vladinator/wow-addon-miniloot.git`. Fetch required refs.

Use the already existing origin/new-features; do not create a replacement remote branch. A local tracking checkout is appropriate. Ensure local master exists tracking origin/master, without changing its contents. Verify remotes, branch relationships, clean working tree, and new-features tracking before infrastructure creation. Finish on new-features.

Before cloning, command-scoped `git -c http.sslBackend=openssl clone ...` may work around Schannel SEC_E_NO_CREDENTIALS because no repository exists yet for local configuration. Once the repository exists, use `git config --local http.sslBackend openssl` and confirm it with `git config --local --get http.sslBackend`. Normal fetch/push operations do not need repeated `-c http.sslBackend=openssl` when that local configuration is present. Never configure this globally or disable `sslVerify`.

Initial setup creates AGENTS.md, the three requested skills and their references, and the external installer at `C:\Users\jonat\Desktop\MiniLoot\atualizar-miniloot.ps1`. Do not change Lua, commit, push, or install during initial setup.
