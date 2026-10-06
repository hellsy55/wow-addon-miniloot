# Local Windows HTTPS fallback only

Load only on local Windows after AGENTS.md's specific HTTPS transport failure occurs; reuse the frozen root and eligibility context. Never load for Cloud or ordinary network/auth errors. Eligibility determined at entry does not trigger extra checks or preventive execution. Perform fallback-specific checks only now, including repository-local http.sslBackend=openssl validation before external execution; failure leaves synchronization PENDENTE. Do not retry HTTPS to classify or validate the failure.

The documented git-remote-https.exe crash, exit 128 with empty stdout/stderr or equivalent transport failure is required; ordinary network/auth errors remain errors. Mark Codex HTTPS transport unavailable for the rest of this execution, including while fallback checks are pending. Do not repeat HTTPS inside Codex, even for verification. Never disable sslVerify, change global credentials/configuration, generate tokens or automatically switch to SSH.

Preserve state and report PENDENTE. Give the exact failed operation in external PowerShell with git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot", preserving all arguments and explicit destination refspecs, for example:

```powershell
git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" fetch --no-tags origin +refs/heads/new-features:refs/remotes/origin/new-features +refs/heads/master:refs/remotes/origin/master
git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" fetch --no-tags upstream +refs/heads/master:refs/remotes/upstream/master
git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" push origin new-features
git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" push origin master
```

Provide only the needed operation and wait for confirmation. GitHub Desktop is an option only for origin operations clearly exposed by its interface, never an assumed equivalent for specific upstream fetches. After external fetch validate local refs read-only. After external push inspect tracking refs; if insufficient request exact external fetch with destination refspec, wait and verify locally. Confirmation alone is not evidence. Resume preparation only after confirmed external fetches, manually using the helper's remaining local checks; do not rerun its network operations in this workflow.

Cloud NEVER uses this fallback: fetch/push/auth/network errors leave it pending, with no external PowerShell or GitHub Desktop request.
