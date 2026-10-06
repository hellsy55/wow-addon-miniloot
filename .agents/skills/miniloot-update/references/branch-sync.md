# Independent branch synchronization

Use the environment-specific validated root from AGENTS.md on EVERY execution. Failure of root, status, branch, ancestry (except documented exit 1), fetch, comparison or publication stops dependent work and leaves it PENDENTE. Never interpret an error as no-op or offer installation on failure.

1. Follow maintenance-runtime.md: resolve Python once and run prepare_update.py --mode update once; authorized Cloud work adds --cloud-work. Reuse its explicitly fetched origin/new-features, origin/master and upstream/master SHAs. No repeated fetch/pull. It rejects unpublished/divergent history before branch mutation, preserves existing local tips and work, and configures tracking. Require real new-features after bootstrap.
2. If new-features is behind origin/new-features, fast-forward with git merge --ff-only origin/new-features. Do not publish preexisting local commits; any ahead/divergent state stops for human review. Recalculate upstream analysis after changing the base. No automatic origin divergence merge.
3. Check git merge-base --is-ancestor upstream/master new-features: exit 0 means no incoming upstream, exit 1 means continue, other exits are errors. Record git merge-base new-features upstream/master and the range <base>..upstream/master; count with git rev-list --count. BEFORE merge, compare paths/modules changed in that range with <base>..new-features. This overlap gate is mandatory when incoming commits exist. Inspect only necessary diffs/code for plausible overlap; use deep_reviewer only per AGENTS.md difficult-case criteria. If upstream introduces libraries/externals, stop for human review.
4. Integrate upstream/master DIRECTLY into new-features with git merge --no-commit upstream/master. Preserve merge semantics. Fast-forward can complete without a commit. A merge commit requires staged name-only, name-status, stat and COMPLETE staged diff without size exceptions, then explicit approval immediately before commit. Prior implementation approval is insufficient. Conflicts always require human choice via merge-conflicts.md; never auto-resolve.
5. Push new-features only with all required commit/publication approvals. Never publish unreviewed previous local commits. Failed push leaves publication pending.
6. Independently synchronize master DIRECTLY from upstream/master. The helper proves origin/master is an ancestor of upstream/master and local master is an ancestor of origin/master; revalidate if state changed. Fast-forward master to origin/master if needed, then upstream/master. Never merge new-features into master or master into new-features; no master merge commit or fork-only history. Push only safe upstream advancement. Avoid checkout if already current.
7. Return to new-features, including after master failures when safe. Verify origin/new-features tip equals the approved local result using the updated tracking ref from successful push; if insufficient, use one explicit verification fetch, not repeated fetches. Report failure as pending.
8. Cloud/Linux: only inform that physical installation is a local Windows step. Never offer installation menu or PowerShell. Local Windows after complete success/no-op shows exactly and waits:

```text
a) instalar MiniLoot agora
b) parar sem instalar
```

Only a authorizes the install skill; update itself never does. Direct installation requests follow that skill.

Complete no-op requires successful checks, local new-features == origin/new-features, local master == origin/master == upstream/master, and upstream/master ancestor of new-features. Unpublished local history or errors never count. Avoid needless checkout, merge, push and semantic analysis.

## Local Windows HTTPS fallback only

Attempt authorized fetch/push normally. Only local Windows, after root and repository-local http.sslBackend=openssl validation, may the documented git-remote-https.exe crash, exit 128 with empty stdout/stderr or equivalent transport failure trigger external execution. Ordinary network/auth errors remain errors. Do not repeat HTTPS inside Codex for the rest of that workflow, even for verification. Never disable sslVerify, change global credentials/configuration, generate tokens or automatically switch to SSH.

Preserve state and report PENDENTE. Give the exact failed operation in external PowerShell with git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot", preserving all arguments and explicit destination refspecs, for example:

```powershell
git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" fetch --no-tags origin +refs/heads/new-features:refs/remotes/origin/new-features +refs/heads/master:refs/remotes/origin/master
git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" fetch --no-tags upstream +refs/heads/master:refs/remotes/upstream/master
git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" push origin new-features
git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" push origin master
```

Provide only the needed operation and wait for confirmation. GitHub Desktop is an option only for origin operations clearly exposed by its interface, never an assumed equivalent for specific upstream fetches. After external fetch validate local refs read-only. After external push inspect tracking refs; if insufficient request exact external fetch with destination refspec, wait and verify locally. Confirmation alone is not evidence. Resume preparation only after confirmed external fetches, manually using the helper's remaining local checks; do not rerun its network operations in this workflow.

Cloud NEVER uses this fallback: fetch/push/auth/network errors leave it pending, with no external PowerShell or GitHub Desktop request.
