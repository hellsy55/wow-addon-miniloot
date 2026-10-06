import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import maintenance_runtime as runtime


class RuntimeTests(unittest.TestCase):
    def test_existing_python(self):
        resolved = runtime.discover()
        self.assertTrue(Path(resolved).is_absolute())
        output = subprocess.check_output([resolved, "-c", "import sys; print(sys.version_info.major)"], text=True)
        self.assertEqual(output.strip(), "3")

    def test_failed_discovery(self):
        with patch.object(runtime.subprocess, "run", side_effect=OSError("unavailable")):
            with self.assertRaisesRegex(RuntimeError, "nothing was installed"):
                runtime.discover()

    def test_reject_bad_candidate(self):
        with patch.object(runtime.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, "missing-python", "")):
            with self.assertRaises(RuntimeError):
                runtime.discover()


if __name__ == "__main__":
    unittest.main()
