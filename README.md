MiniLoot
==================
Tired of the amount of messages related to looting items, reputation, experience, money, and so forth? If that is the case then this is the addon for you! MiniLoot is designed to summarize these type of messages in concise one-liners.

Features
------------------
- Interface options for easy customization.
- Change how messages and item icons appear.
- Include bag and bank item in the item counter.
- Mark items with appearances you have not yet collected.
- Hide junk items, set filters for what quality of items are shown when soloing, in party or raids.
- Show artifact power as loot instead of the default message.
- Shorten faction names when standing changes.
- Show tooltips when you mouseover links in chat.

Local validation before committing
------------------
After applying an incremental ZIP, validate the current working tree (including
new and uncommitted Lua files), then review it in GitHub Desktop. Validation does
not stage files, synchronize branches, install the addon, or publish anything.

On this Windows checkout, first verify the root and branch with the installed Git:

```powershell
$repo = 'C:\Users\jonat\Desktop\MiniLoot\Github\wow-addon-miniloot'
$git = 'C:\Program Files\Git\cmd\git.exe'
$actualRoot = & $git -C $repo rev-parse --show-toplevel
if ($LASTEXITCODE -ne 0) { throw 'Cannot identify the repository' }
if ([IO.Path]::GetFullPath($actualRoot) -ne [IO.Path]::GetFullPath($repo)) {
    throw 'Unexpected repository root'
}
$branch = & $git -C $repo symbolic-ref --short HEAD
if ($LASTEXITCODE -ne 0 -or $branch -ne 'new-features') {
    throw 'Validation procedure requires new-features'
}
& $git -C $repo status --short --branch
if ($LASTEXITCODE -ne 0) { throw 'Cannot inspect the working tree' }
Set-Location -LiteralPath $repo
```

Use a real existing Python 3 executable; do not assume the `py -3` launcher works.
The existing discovery helper reports the runtime without installing anything:

```powershell
# Adjust only if your existing Python installation uses another location.
$candidatePython = 'C:\Users\jonat\AppData\Local\Programs\Python\Python312\python.exe'
$runtimeJson = & $candidatePython -B scripts/maintenance_runtime.py
if ($LASTEXITCODE -ne 0) { throw 'Python discovery failed' }
$python = ($runtimeJson | ConvertFrom-Json).python
if (-not $python) { throw 'No Python runtime returned' }
& $python --version
```

Provide the absolute path of a previously obtained, trusted **Lua 5.1 compiler**.
The following path is a placeholder, not a tool installed by this project:

```powershell
$luac = 'C:\Tools\Lua51\luac.exe' # Replace with your verified executable.
if (-not (Test-Path -LiteralPath $luac -PathType Leaf)) {
    throw 'Lua 5.1 compiler is unavailable; full validation cannot run'
}
& $python -B scripts/validate_addon.py --luac $luac
if ($LASTEXITCODE -ne 0) { throw 'Addon validation failed' }
$previousTestLuac = $env:MINILOOT_TEST_LUAC
try {
    $env:MINILOOT_TEST_LUAC = $luac
    & $python -B -m unittest discover -s scripts/tests -v
    if ($LASTEXITCODE -ne 0) { throw 'Python tests failed' }
} finally {
    $env:MINILOOT_TEST_LUAC = $previousTestLuac
}
```

The validator checks the actual compiler banner and rejects other Lua versions
and LuaJIT. It invokes `-p` separately for every Lua source without executing the
addon or writing bytecode. No global installation or permanent PATH change is
performed. Without a compiler, `--structure-only` explicitly reports a partial
manifest check; it is not full validation. The real-compiler test is skipped when
`MINILOOT_TEST_LUAC` is unset. Never interpret that skip as a successful Lua check.

The three manifests must reference existing files with exact capitalization,
safe relative paths, no duplicates, and identical non-empty load sequences. New
modules are allowed when added consistently. Interface and Version may differ.
The known SavedVariables declarations are preserved, including legacy
`MiniLootDB`; an authorized migration must deliberately update the validator's
contract and tests. Personal files in `WTF` are never inspected or rewritten.

Tests use disposable temporary repositories, including local fixture commits,
pushes, merges and configuration. They do not run maintenance against this
checkout or contact the real remotes. Do not invoke `prepare_update.py` as a
validation command. Use `-B` to avoid Python bytecode in the checkout.

Record the base SHA with `& $git -C $repo rev-parse HEAD`, the current status and
tool versions when reviewing results. Local results cover the working tree, not
just HEAD; any subsequent edit requires revalidation. GitHub Actions independently
checks out the event SHA, verifies the extracted SHA and logs tool versions. Its
single read-only validation job runs on relevant pushes to `new-features` and
manual dispatch on that branch. Documentation-only pushes are skipped. It does
not gate or change the separate tag-based release workflow.

These checks detect syntax and package-structure errors, not correct WoW API use,
loot behavior, UI behavior, persistence migrations or compatibility with every
game client. Test relevant behavior in WoW before installing or publishing.
