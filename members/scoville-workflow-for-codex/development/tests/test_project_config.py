"""Project overrides reach actual model consumers; legacy role settings are inert."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

from test_contract import PACKAGE
sys.path.insert(0, str(PACKAGE / "scripts"))
from resolve_model_pair import load_config, resolve


class ProjectConfigTests(unittest.TestCase):
    def test_explorer_inherits_effective_executor_with_independent_field_overrides(self):
        defaults = PACKAGE / 'assets/workflow.toml'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / '.scoville').mkdir()
            path = root / '.scoville/config.json'
            saved = {'workflow': {'execute': {'low': {'model': 'executor-custom', 'reasoning': 'high'}},
                                  'explore': {'low': {'reasoning': 'medium'}}}}
            path.write_text(json.dumps(saved), encoding='utf-8')
            config = load_config(defaults, root)
            self.assertEqual(resolve(config, 'explorer', 'low')['model'], 'executor-custom')
            self.assertEqual(resolve(config, 'explorer', 'low')['thinking'], 'medium')
            self.assertEqual(resolve(config, 'executor', 'low')['thinking'], 'high')
            self.assertEqual(config['explore']['medium'], config['execute']['medium'])
            saved['workflow']['execute']['low']['model'] = 'updated-executor'
            path.write_text(json.dumps(saved), encoding='utf-8')
            self.assertEqual(resolve(load_config(defaults, root), 'explorer', 'low')['model'], 'updated-executor')
            self.assertEqual(json.loads(path.read_text()), saved)

    def test_partial_file_overrides_and_ephemeral_model_choice(self):
        defaults = PACKAGE / "assets/workflow.toml"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original = load_config(defaults, root)
            self.assertEqual(set(original), {'schema_version', 'execute', 'review', 'explore'})
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
            self.assertNotIn("context", config)
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


    def test_legacy_fields_are_ignored_without_rewriting_project(self):
        defaults = PACKAGE / 'assets/workflow.toml'
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / '.scoville').mkdir()
            path = root / '.scoville/config.json'
            baseline = load_config(defaults, root)
            for value in (None, [], False, {'worker_percent': 'broken', 'secret': 'not-read'}):
                saved = {'workflow': {'manager': value, 'context': value, 'pin_threads': value},
                         'other': {'keep': True}}
                path.write_text(json.dumps(saved), encoding='utf-8')
                before = path.read_bytes()
                with self.subTest(value=value):
                    self.assertEqual(load_config(defaults, root), baseline)
                    self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
