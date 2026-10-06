"""Discover an existing Python 3 runtime without installing anything."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


def discover():
    candidates = [[sys.executable]] if sys.executable else []
    for name in ("python3", "python", "py"):
        executable = shutil.which(name)
        if executable:
            candidates.append([executable] + (["-3"] if name == "py" else []))
    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python"
        candidates.extend([str(p)] for p in sorted(base.glob("Python*/python.exe")))
    for candidate in candidates:
        try:
            result = subprocess.run(candidate + ["-c", "import sys; assert sys.version_info.major == 3; print(sys.executable)"],
                                    capture_output=True, text=True, timeout=10, check=True)
            runtime = Path(result.stdout.strip()).resolve(strict=True)
            if runtime.is_file():
                return str(runtime)
        except (OSError, ValueError, subprocess.SubprocessError):
            continue
    raise RuntimeError("Cannot determine an existing Python 3 runtime; nothing was installed")


if __name__ == "__main__":
    try:
        print(json.dumps({"python": discover()}))
    except RuntimeError as error:
        print(json.dumps({"error": str(error)}))
        sys.exit(1)
