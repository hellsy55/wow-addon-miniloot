"""Read-only MiniLoot manifest and Lua 5.1 syntax validation."""
import argparse
import os
from pathlib import Path, PureWindowsPath
import re
import subprocess
import sys

MANIFESTS = ("MiniLoot.toc", "MiniLoot_Classic.toc", "MiniLoot_Vanilla.toc")
# Change this contract only as part of an explicitly reviewed persistence migration.
SAVED_VARIABLES = {"MiniLootDB", "MiniLootDB2", "MiniLootRemixDB2"}


class ValidationError(ValueError):
    pass


def exact_file(root, entry):
    """Check each component by directory enumeration, even on Windows."""
    normalized = entry.replace("\\", "/")
    if PureWindowsPath(entry).drive or normalized.startswith("/"):
        raise ValidationError(f"absolute path is forbidden: {entry}")
    parts = normalized.split("/")
    if any(part in ("", ".", "..") or ":" in part for part in parts):
        raise ValidationError(f"unsafe path component: {entry}")
    current = root
    for part in parts:
        names = {child.name for child in current.iterdir()}
        if part not in names:
            similar = next((name for name in names if name.casefold() == part.casefold()), None)
            reason = f"capitalization mismatch (found {similar})" if similar else "missing file or directory"
            raise ValidationError(f"{reason}: {entry}")
        current = current / part
        if not current.resolve().is_relative_to(root):
            raise ValidationError(f"path escapes addon root: {entry}")
    if not current.is_file():
        raise ValidationError(f"not a regular file: {entry}")
    return normalized


def validate_manifests(root):
    root = Path(root).resolve()
    sequences = {}
    for name in MANIFESTS:
        try:
            exact_file(root, name)
            files, saved = [], []
            for line_number, line in enumerate((root / name).read_text(encoding="utf-8-sig").splitlines(), 1):
                line = line.strip()
                if not line:
                    continue
                if line.startswith("#"):
                    match = re.fullmatch(r"##\s*SavedVariables\s*:\s*(.*)", line, re.IGNORECASE)
                    if match:
                        saved.append([value.strip() for value in match[1].split(",")])
                    continue
                try:
                    entry = exact_file(root, line)
                    if entry.casefold() in {value.casefold() for value in files}:
                        raise ValidationError(f"duplicate load entry: {line}")
                    files.append(entry)
                except (OSError, ValidationError) as error:
                    raise ValidationError(f"line {line_number}: {error}") from None
            if len(saved) != 1 or len(saved[0]) != len(SAVED_VARIABLES) or set(saved[0]) != SAVED_VARIABLES:
                raise ValidationError(f"SavedVariables must declare exactly {', '.join(sorted(SAVED_VARIABLES))}")
            if not files:
                raise ValidationError("empty load sequence")
            sequences[name] = files
        except (OSError, UnicodeError, ValidationError) as error:
            raise ValidationError(f"{name}: {error}") from None
    baseline = sequences[MANIFESTS[0]]
    for name, files in sequences.items():
        if files != baseline:
            raise ValidationError(f"{name}: load sequence differs from {MANIFESTS[0]}: {files!r} != {baseline!r}")
    return sequences


def lua_files(root):
    """Include new/untracked Lua sources; exclude Git metadata, never follow links."""
    result = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        base = Path(directory)
        for name in dirs + files:
            path = base / name
            if name != ".git" and path.is_symlink():
                raise ValidationError(f"symlink is not supported in addon sources: {path.relative_to(root)}")
        dirs[:] = sorted(name for name in dirs if name != ".git")
        result.extend(base / name for name in sorted(files) if name.lower().endswith(".lua"))
    return sorted(result)


def compile_lua(root, executable):
    def run(arguments):
        try:
            return subprocess.run([str(executable), *arguments], cwd=root, capture_output=True,
                                  text=True, errors="replace", timeout=30, shell=False)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise ValidationError(f"Lua 5.1 compiler unavailable or timed out ({executable}): {error}") from None

    version = run(["-v"])
    banner = (version.stdout + version.stderr).strip()
    if version.returncode != 0 or not re.fullmatch(r"Lua 5\.1(?:\.\d+)?\s+Copyright\b[^\r\n]*", banner):
        raise ValidationError(f"expected official Lua 5.1 compiler, got exit {version.returncode}: {banner!r}")
    files = lua_files(root)
    if not files:
        raise ValidationError("no Lua source files found")
    errors = []
    for path in files:
        result = run(["-p", "--", str(path)])
        if result.returncode != 0:
            errors.append(f"{path.relative_to(root)}: exit {result.returncode}: "
                          + (result.stderr + result.stdout).strip())
    if errors:
        raise ValidationError("Lua syntax validation failed:\n" + "\n".join(errors))
    return banner, len(files)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--luac", help="Trusted Lua 5.1 compiler executable (absolute path recommended)")
    mode.add_argument("--structure-only", action="store_true", help="Check manifests only; does not validate Lua syntax")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        sequences = validate_manifests(root)
        print(f"Manifests OK: {len(sequences)} variants, {len(sequences[MANIFESTS[0]])} load entries each")
        if args.structure_only:
            print("PARTIAL: Lua syntax was not checked (--structure-only)")
        else:
            version, count = compile_lua(root, args.luac)
            print(f"Compiler: {version}\nLua syntax OK: {count} files (individual -p checks)")
        print("Validation does not execute the addon or verify WoW behavior.")
        return 0
    except (OSError, UnicodeError, ValidationError) as error:
        print(f"Validation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
