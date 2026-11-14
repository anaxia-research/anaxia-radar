import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class StandaloneTests(unittest.TestCase):
    def run_module(self, *arguments, cwd=ROOT):
        environment = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONDONTWRITEBYTECODE="1")
        return subprocess.run([sys.executable, "-m", "anaxia_radar", *map(str, arguments)],
                              cwd=cwd, env=environment, capture_output=True, text=True)

    def test_module_entry_point(self):
        result = self.run_module("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("refresh", result.stdout)
        self.assertIn("show", result.stdout)

    def test_offline_runs_outside_repository_with_packaged_config(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_module("refresh", "--offline", ROOT / "examples/radar-fixture.json",
                                     cwd=directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            snapshot = json.loads((Path(directory) / "data/research-radar.json").read_text())
            self.assertEqual(snapshot["mode"], "offline_fixture")
            self.assertEqual(snapshot["summary"]["candidates"], 1)
            self.assertIn("Offline demonstration", (Path(directory) / "docs/RESEARCH-RADAR.md").read_text())
            self.assertFalse((Path(directory) / "config/research-watch.json").exists())

    def test_show_accepts_explicit_snapshot_from_another_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            result = self.run_module("show", "--input", ROOT / "data/research-radar.json", cwd=directory)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["mode"], "live")


if __name__ == "__main__":
    unittest.main()
