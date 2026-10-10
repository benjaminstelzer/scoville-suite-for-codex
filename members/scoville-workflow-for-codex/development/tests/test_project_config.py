"""Project overrides reach the actual model and context consumers."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

from test_contract import PACKAGE
sys.path.insert(0, str(PACKAGE / "scripts"))
from resolve_model_pair import load_config, resolve
from check_context_checkpoint import read_thresholds


class ProjectConfigTests(unittest.TestCase):
    def test_partial_file_overrides_and_ephemeral_model_choice(self):
        defaults = PACKAGE / "assets/workflow.toml"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = load_config(defaults, root)
            self.assertEqual(original['manager'], {'model': 'gpt-6.1-sol', 'reasoning': 'high'})
            self.assertFalse((root / ".scoville").exists())
            (root / ".scoville").mkdir()
            path = root / ".scoville/config.json"
            saved = {"workflow": {"execute": {"low": {"model": "custom-model"}},
                                  "context": {"worker_percent": 80}}}
            path.write_text(json.dumps(saved), encoding="utf-8")
            config = load_config(defaults, root)
            self.assertEqual(config["execute"]["low"]["model"], "custom-model")
            self.assertEqual(config["execute"]["low"]["reasoning"], original["execute"]["low"]["reasoning"])
            self.assertEqual(config["review"], original["review"])
            self.assertEqual(read_thresholds(defaults, root)["worker_percent"], 80)
            self.assertEqual(resolve(config, "executor", "low", "one-call")["model"], "one-call")
            self.assertEqual(json.loads(path.read_text()), saved)
            child = root / "child"
            child.mkdir()
            self.assertEqual(load_config(defaults, child), original)
            saved["workflow"]["execute"]["low"]["model"] = "next-run"
            path.write_text(json.dumps(saved), encoding="utf-8")
            self.assertEqual(load_config(defaults, root)["execute"]["low"]["model"], "next-run")

    def test_invalid_values_fail_in_the_consuming_operation(self):
        defaults = PACKAGE / "assets/workflow.toml"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".scoville").mkdir()
            path = root / ".scoville/config.json"
            for value in (None, [], {"execute": {"low": {"reasoning": False}}}):
                path.write_text(json.dumps({"workflow": value}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_config(defaults, root)
            for value in (False, 0, 100, 33.5, "75"):
                path.write_text(json.dumps({"workflow": {"context": {"worker_percent": value}}}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    read_thresholds(defaults, root)

    def test_threshold_diagnostic_identifies_and_repairs_field(self):
        defaults = PACKAGE / 'assets/workflow.toml'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / '.scoville').mkdir()
            path = root / '.scoville/config.json'
            path.write_text(json.dumps({'workflow': {'context': {'worker_percent': '60'}}}), encoding='utf-8')
            with self.assertRaises(ValueError) as failure:
                read_thresholds(defaults, root)
            self.assertIn('worker_percent', str(failure.exception))
            self.assertIn('without percent signs or quotes', str(failure.exception))
            path.write_text(json.dumps({'workflow': {'context': {'worker_percent': 60}}}), encoding='utf-8')
            self.assertEqual(read_thresholds(defaults, root)['worker_percent'], 60)

    def test_invalid_pair_does_not_echo_private_value(self):
        import subprocess
        marker = 'TEST_PRIVATE_VALUE_NOT_FOR_DIAGNOSTICS'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / '.scoville').mkdir()
            path = root / '.scoville/config.json'
            path.write_text(json.dumps({'workflow': {'execute': {'low': {'api_key': marker}}}}), encoding='utf-8')
            cmd = [sys.executable, str(PACKAGE / 'scripts/resolve_model_pair.py'), '--role', 'executor',
                   '--route', 'low', '--project-root', str(root)]
            failed = subprocess.run(cmd, text=True, encoding='utf-8', capture_output=True)
            self.assertEqual(failed.returncode, 1)
            self.assertNotIn(marker, failed.stdout + failed.stderr)
            self.assertIn('execute.low', failed.stdout)
            path.write_text('{}', encoding='utf-8')
            corrected = subprocess.run(cmd, text=True, encoding='utf-8', capture_output=True)
            self.assertEqual(corrected.returncode, 0, corrected.stdout)

    def test_manager_pair_validation_and_partial_manual_overrides(self):
        defaults = PACKAGE / 'assets/workflow.toml'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / '.scoville').mkdir()
            path = root / '.scoville/config.json'
            for pair in (None, [], {'model': False}, {'model': '  '},
                         {'model': 'one\ntwo'}, {'reasoning': 'bad'},
                         {'reasoning': False}, {'token': 'private-value'}):
                path.write_text(json.dumps({'workflow': {'manager': pair}}), encoding='utf-8')
                with self.subTest(pair=pair), self.assertRaisesRegex(ValueError, 'workflow.manager'):
                    load_config(defaults, root)
            path.write_text(json.dumps({'workflow': {'manager': {'reasoning': 'ultra'}}}), encoding='utf-8')
            self.assertEqual(load_config(defaults, root)['manager'],
                             {'model': 'gpt-6.1-sol', 'reasoning': 'ultra'})


if __name__ == "__main__":
    unittest.main()
