# Independent branch synchronization

Every Git command below must explicitly target `C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot`: set that working directory on EVERY execution or use `git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" ...`. Never assume the session directory or rely on a previous execution's `cd`.

Mandatory failure gate: a failed root preflight, status, branch detection, ancestry check (other than its documented exit 1), fetch, or any other required verification stops dependent operations. Report the update as PENDENTE, never completed or a no-op; do not offer installation or run the installer. In particular, "not a git repository" must never lead to fetch, merge, push, the installation menu, or installation. Step 9 is reachable only after ALL required synchronization succeeds or the complete no-op conditions below are proven.

1. First run `git rev-parse --show-toplevel` against the explicit repository directory and verify that the resolved root is `C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot`. STOP if it fails or differs. Then inspect current branch and working tree once; STOP if either check fails. Stop for unexpected changes or an unfinished Git operation. Use new-features for development integration.
2. Use repository-local `http.sslBackend=openssl`; check it with `git config --local --get http.sslBackend` and configure it only locally if needed. Normal fetch/push commands need no repeated command-scoped override. Never change the global SSL configuration or disable `sslVerify`. Fetch origin and upstream once each. Stop on any failed fetch; reuse fetched refs thereafter.
3. Compare new-features against origin/new-features using ahead/behind counts. If behind only, fast-forward to origin/new-features. If ahead before the update, stop and review unpublished commits; require explicit authorization before any publication and do not publish automatically. If divergent, use `git merge --no-commit origin/new-features`. Follow merge-conflicts.md for conflicts. For a clean merge requiring a commit, show the complete staged file list, staged stat, and COMPLETE staged diff and wait for explicit approval immediately before committing. Never force-push or discard history. After any integration of origin/new-features that changes the base, recalculate the pending upstream range before upstream analysis or integration.
4. Test ancestry with `git merge-base --is-ancestor upstream/master new-features`: exit 0 means upstream/master is already incorporated and there is no incoming upstream; exit 1 means continue; any other exit is an error, not a no-op. Otherwise record the successful `git merge-base new-features upstream/master` result and use exactly `<merge-base>..upstream/master` as the pending upstream range. Count its commits with `git rev-list --count <merge-base>..upstream/master`; ancestry, merge-base, or rev-list errors stop the stage. Use that SAME recorded base for the cheap overlap gate: compare changed paths/modules in `<merge-base>..upstream/master` with relevant local customization paths in `<merge-base>..new-features`. If origin/new-features integration changes the merge-base, recompute the range and count before using them. If no plausible overlap exists, avoid deep semantic analysis. For overlap, open only necessary diffs and code.
5. Integrate upstream/master DIRECTLY into new-features, retaining merge semantics. Use `git merge --no-commit upstream/master`; a fast-forward may complete without a commit. For a merge commit, stop at the complete AGENTS.md staged review checkpoint and wait for explicit commit approval. Never create that commit automatically. For conflicts, follow merge-conflicts.md and do not resolve automatically.
6. Push new-features only after all necessary commit and publication approvals, including approval for any preexisting unpublished commits. A failed push leaves publication pending.
7. Synchronize master independently. Before advancing, prove origin/master contains no fork-only history that prevents a safe upstream fast-forward. Verify local master against origin/master and upstream/master; stop for divergence or fork customizations. Fast-forward local master to origin/master if needed, then directly to upstream/master. Never merge new-features or create a master merge commit. Push master only as a safe upstream advancement within the authorized update. Do not push unrelated local history.
8. Return to new-features after any master checkout, including when a master stage fails if safe to do so. If master is already current, avoid checkout entirely.
9. Verify the published origin/new-features tip equals the approved new-features result. After every successful synchronization, INCLUDING a complete no-op, ALWAYS present exactly:

   ```text
   a) instalar MiniLoot agora
   b) parar sem instalar
   ```

   STOP waiting for the user's response. Only an explicit installation choice authorizes loading the install skill and running `powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\jonat\Desktop\MiniLoot\atualizar-miniloot.ps1"`. Update requests authorize ONLY Git synchronization; never infer installation authorization from completion, no-op, an updated origin/new-features, completed commits/pushes, or remote ZIP availability. Only an unequivocal direct installation request bypasses the menu.

A complete no-op requires all necessary Git comparisons to succeed, local new-features == origin/new-features, local master == origin/master, upstream/master already incorporated into new-features by ancestry, and master already equal to upstream/master under its upstream-only fast-forward rules. Only then avoid checkout, merge, push, repeated status, and unnecessary semantic analysis and report a compact no-op, followed by the mandatory step 9 menu and wait. Unpublished local-ahead history never counts as a no-op. Never interpret an error as a no-op.

## Codex HTTPS transport failure

Attempt authorized fetch/push normally inside Codex. Useful remote error messages follow normal error handling. Only after validating the repository root and local `http.sslBackend=openssl`, a `git-remote-https.exe` crash, exit 128 with empty stdout/stderr, or equivalent Codex HTTPS transport failure triggers the AGENTS.md external-execution fallback. Codex HTTPS transport is then unavailable for the REST of that workflow execution: do not perform another HTTPS fetch/push inside Codex, even to verify external execution. Preserve all local state; never retry in a loop, disable `sslVerify`, change `credential.helper` or global Git configuration, generate a token, or automatically switch to SSH.

Report remote synchronization/publication as PENDENTE. Provide ONLY the exact operation needed in normal PowerShell outside Codex (preserve the exact refs and additional arguments of the failed fetch, including upstream operations):

```powershell
git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" push origin new-features
git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" push origin master
git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" fetch origin
git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" fetch upstream
```

For origin push/fetch, mention GitHub Desktop only when the equivalent operation is available in its interface. For operations not clearly exposed there, such as a specific upstream fetch, use the supplied PowerShell command. Never assume Desktop performed an operation different from the one the user confirmed.

STOP waiting for confirmation of external execution, then recover as follows:

- External fetch: the fetch itself updated local remote-tracking refs. Verify ONLY with local read-only Git checks (`rev-parse`, ancestry, ahead/behind, `rev-list`, and other required comparisons). Do not fetch again inside Codex.
- External push: first inspect the corresponding local remote-tracking ref. Continue only if local read-only comparisons sufficiently prove the published tip matches the approved result. If the ref is not updated or local evidence is insufficient, request the exact fetch outside Codex, STOP waiting for confirmation, then validate ONLY with local comparisons. For new-features use `git -C "C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot" fetch origin new-features`; for master use the equivalent with `master`. Preserve exact necessary refs/arguments for upstream operations. Never fetch inside Codex in this execution.

Until every necessary external operation is confirmed AND sufficiently verified locally, remain PENDENTE: no dependent integration, installation menu, or installation. User confirmation alone is not proof without sufficient local Git state. Do not show the installation menu until origin/new-features is verified to contain exactly the approved result and all required synchronization has completed.
