"""Isolated validation fixtures; real compiler checks require MINILOOT_TEST_LUAC."""
import contextlib
import hashlib
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import validate_addon as validator

ROOT = Path(__file__).resolve().parents[2]


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "addon with spaces"
        self.root.mkdir()
        self.source = "local value = ...\n"
        for name in ("first.lua", "second.lua"):
            (self.root / name).write_text(self.source, encoding="utf-8")
        self.header = ("# comment\n## Title: MiniLoot\n"
                       "## SavedVariables: MiniLootDB, MiniLootDB2, MiniLootRemixDB2\n")
        self.write_manifests()

    def write_manifests(self, sequence="first.lua\nsecond.lua\n"):
        for index, name in enumerate(validator.MANIFESTS):
            (self.root / name).write_text(self.header + f"## Interface: {index + 1}\n"
                                         + f"## Version: {index}.0\n\n" + sequence, encoding="utf-8")

    def rejected(self, text):
        with self.assertRaisesRegex(validator.ValidationError, text):
            validator.validate_manifests(self.root)

    def invoke(self, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            code = validator.main(["--root", str(self.root), *args])
        return code, output.getvalue()

    def test_current_repository_structure(self):
        sequences = validator.validate_manifests(ROOT)
        self.assertEqual(set(sequences), set(validator.MANIFESTS))
        self.assertTrue(sequences[validator.MANIFESTS[0]])

    def test_variants_allow_different_metadata(self):
        validator.validate_manifests(self.root)

    def test_missing_manifest(self):
        (self.root / validator.MANIFESTS[1]).unlink()
        self.rejected("MiniLoot_Classic.toc.*missing")

    def test_missing_source(self):
        (self.root / "first.lua").unlink()
        self.rejected("MiniLoot.toc.*line.*missing.*first.lua")

    def test_case_mismatch(self):
        self.write_manifests("FIRST.lua\nsecond.lua\n")
        self.rejected("capitalization mismatch")

    def test_nested_paths_and_comments(self):
        (self.root / "Modules").mkdir()
        (self.root / "Modules" / "new file.lua").write_text(self.source)
        self.write_manifests("# ignored.lua\nModules\\new file.lua\nfirst.lua\n")
        self.assertEqual(validator.validate_manifests(self.root)[validator.MANIFESTS[0]][0],
                         "Modules/new file.lua")
        self.write_manifests("modules/new file.lua\n")
        self.rejected("capitalization mismatch")

    def test_absolute_and_escaping_paths(self):
        for path in ("/tmp/file.lua", "C:\\file.lua", "C:file.lua", "\\\\server\\share\\file.lua",
                     "../file.lua", "Modules/../../file.lua", "first.lua:stream"):
            with self.subTest(path=path):
                self.write_manifests(path + "\n")
                self.rejected("absolute|unsafe")

    def test_duplicate_entry(self):
        self.write_manifests("first.lua\nfirst.lua\n")
        self.rejected("duplicate")

    def test_order_mismatch(self):
        (self.root / validator.MANIFESTS[2]).write_text(self.header + "second.lua\nfirst.lua\n")
        self.rejected("MiniLoot_Vanilla.toc.*load sequence differs")

    def test_new_module_is_allowed(self):
        (self.root / "new.lua").write_text(self.source)
        self.write_manifests("first.lua\nnew.lua\nsecond.lua\n")
        self.assertEqual(len(validator.validate_manifests(self.root)[validator.MANIFESTS[0]]), 3)

    def test_saved_variables_contract(self):
        for declaration in ("", "## SavedVariables: MiniLootDB2, MiniLootRemixDB2\n",
                            "## SavedVariables: MiniLootDB, MiniLootDB2, RenamedDB\n",
                            self.header + self.header):
            with self.subTest(declaration=declaration):
                (self.root / validator.MANIFESTS[0]).write_text(declaration + "first.lua\nsecond.lua\n")
                self.rejected("SavedVariables")

    def test_bom_and_crlf(self):
        for name in validator.MANIFESTS:
            path = self.root / name
            path.write_bytes(b"\xef\xbb\xbf" + path.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        validator.validate_manifests(self.root)

    def test_empty_load_sequence(self):
        self.write_manifests("")
        self.rejected("empty load sequence")

    def test_compiler_missing_returns_failure(self):
        code, output = self.invoke("--luac", str(self.root / "missing-luac"))
        self.assertEqual(code, 1)
        self.assertIn("unavailable", output)

    def test_wrong_compiler_rejected_before_compilation(self):
        for banner in ("Lua 5.2.4 Copyright", "Lua 5.3.6 Copyright", "Lua 5.4.8 Copyright",
                       "LuaJIT 2.1", "Lua 5.1 Copyright\nLuaJIT"):
            with self.subTest(banner=banner), patch.object(validator.subprocess, "run", return_value=
                    subprocess.CompletedProcess([], 0, banner, "")) as run:
                code, _ = self.invoke("--luac", "trusted-luac")
                self.assertEqual(code, 1)
                self.assertEqual(run.call_count, 1)

    def compiler_result(self, command, **kwargs):
        if command[1:] == ["-v"]:
            return subprocess.CompletedProcess(command, 0, "", "Lua 5.1.5  Copyright (C) 1994-2012 Lua.org, PUC-Rio\n")
        self.assertEqual(command[1:3], ["-p", "--"])
        self.assertFalse(kwargs["shell"])
        self.assertEqual(Path(kwargs["cwd"]), self.root)
        return subprocess.CompletedProcess(command, 0, "", "")

    def test_individual_compilation_includes_new_unlisted_sources(self):
        (self.root / "new.lua").write_text(self.source)
        with patch.object(validator.subprocess, "run", side_effect=self.compiler_result) as run:
            code, output = self.invoke("--luac", "trusted-luac")
        self.assertEqual(code, 0)
        self.assertEqual(run.call_count, 4)
        self.assertIn("3 files", output)

    def test_syntax_diagnostic_propagates(self):
        def result(command, **kwargs):
            checked = self.compiler_result(command, **kwargs)
            if command[-1].endswith("first.lua"):
                return subprocess.CompletedProcess(command, 1, "", "first.lua:2: unexpected symbol near '='")
            return checked
        with patch.object(validator.subprocess, "run", side_effect=result):
            code, output = self.invoke("--luac", "trusted-luac")
        self.assertEqual(code, 1)
        self.assertIn("first.lua:2", output)

    def test_compiler_timeout(self):
        with patch.object(validator.subprocess, "run", side_effect=subprocess.TimeoutExpired("luac", 30)):
            self.assertEqual(self.invoke("--luac", "trusted-luac")[0], 1)

    def test_failed_version_command_is_rejected(self):
        with patch.object(validator.subprocess, "run", return_value=subprocess.CompletedProcess(
                [], 1, "Lua 5.1.5 Copyright", "")) as run:
            self.assertEqual(self.invoke("--luac", "trusted-luac")[0], 1)
        self.assertEqual(run.call_count, 1)

    def test_manifest_failure_returns_nonzero_without_compiler(self):
        (self.root / "first.lua").unlink()
        with patch.object(validator.subprocess, "run", side_effect=AssertionError("compiler launched")):
            code, output = self.invoke("--luac", "trusted-luac")
        self.assertEqual(code, 1)
        self.assertIn("first.lua", output)

    def test_structure_only_is_explicitly_partial(self):
        code, output = self.invoke("--structure-only")
        self.assertEqual(code, 0)
        self.assertIn("PARTIAL", output)

    def test_validation_preserves_source_bytes(self):
        def snapshot():
            return {p.relative_to(self.root): hashlib.sha256(p.read_bytes()).digest()
                    for p in self.root.rglob("*") if p.is_file()}
        before = snapshot()
        with patch.object(validator.subprocess, "run", side_effect=self.compiler_result):
            self.assertEqual(self.invoke("--luac", "trusted-luac")[0], 0)
        self.assertEqual(snapshot(), before)

    @unittest.skipUnless(os.environ.get("MINILOOT_TEST_LUAC"), "MINILOOT_TEST_LUAC not configured; real Lua compiler unavailable")
    def test_real_compiler_valid_and_invalid_lua(self):
        compiler = os.environ["MINILOOT_TEST_LUAC"]
        code, output = self.invoke("--luac", compiler)
        self.assertEqual(code, 0, output)
        (self.root / "first.lua").write_text("local = broken\n")
        code, output = self.invoke("--luac", compiler)
        self.assertEqual(code, 1, output)
        self.assertIn("first.lua:1", output)


if __name__ == "__main__":
    unittest.main()
