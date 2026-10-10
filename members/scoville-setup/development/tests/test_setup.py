"""Exercise shipped Setup, legacy config migration and real route consumers."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[4]
spec = importlib.util.spec_from_file_location('setup_builder', ROOT / 'development/build_suite.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name)
        config = builder.load(ROOT, 'codex', 'suite')
        for name in ('scoville-setup', 'scoville-ask-for-codex', 'scoville-workflow-for-codex'):
            member = next(m for m in config['members'] if m['name'] == name)
            for relative, data in builder.payload(ROOT, member, config).items():
                target = self.base / name / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
        self.project = self.base / 'Projekt Ä 中文'
        self.project.mkdir()
        self.path = self.project / '.scoville/config.json'
        self.helper = self.base / 'scoville-setup/scoville-setup/scripts/setup.py'
        self.workflow = self.base / 'scoville-workflow-for-codex/scoville-workflow-for-codex/scripts'

    def save(self, value):
        self.path.parent.mkdir(exist_ok=True)
        self.path.write_text(json.dumps(value, ensure_ascii=False) + '\n', encoding='utf-8')

    def run_setup(self, operation, patch=None, raw=None):
        result = subprocess.run([sys.executable, '-B', str(self.helper), operation,
                                 '--project-root', str(self.project)],
                                input=raw if raw is not None else json.dumps(patch, ensure_ascii=False).encode('utf-8'),
                                capture_output=True)
        return result.returncode, json.loads(result.stdout.decode('utf-8'))

    def test_show_ignores_legacy_fields_without_writing(self):
        status, shown = self.run_setup('show')
        self.assertEqual(status, 0)
        self.assertFalse(self.path.parent.exists())
        self.save({'workflow': {'context': {'worker_percent': 'obsolete'},
                                'manager': {'model': False}, 'pin_threads': 'obsolete'},
                   'unrelated': {'keep': 'Ä 中文'}})
        before = self.path.read_bytes()
        status, shown = self.run_setup('show')
        self.assertEqual(status, 0)
        self.assertFalse(shown['saved'])
        self.assertEqual(set(shown['effective']['workflow']), {'schema_version', 'execute', 'review', 'explore'})
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(shown['effective']['workflow']['review']['medium'],
                         {'model': 'gpt-6.1-sol', 'reasoning': 'high'})

    def test_authorized_save_removes_only_workflow_legacy_fields(self):
        before = {'workflow': {'context': {'worker_percent': 82}, 'manager': {'model': 'old'},
                               'pin_threads': False,
                               'execute': {'low': {'model': 'gpt-6.1-sol', 'reasoning': 'low'}},
                               'review': {'low': {'model': 'gpt-6.1-sol', 'reasoning': 'medium'}}},
                  'ask': {'pin_threads': True, 'claude': {'timeout_seconds': 2400}},
                  'other_tool': {'keep': [1, 2, 'Ä 中文']}}
        self.save(before)
        status, saved = self.run_setup('set', {'workflow': {'execute': {'low': {'reasoning': 'medium'}}}})
        self.assertEqual(status, 0, saved)
        after = json.loads(self.path.read_text(encoding='utf-8'))
        expected = json.loads(json.dumps(before))
        for key in ('context', 'manager', 'pin_threads'):
            expected['workflow'].pop(key)
        expected['workflow']['execute']['low']['reasoning'] = 'medium'
        self.assertEqual(after, expected)
        self.assertTrue(saved['saved'])
        resolved = subprocess.run([sys.executable, '-B', str(self.workflow / 'resolve_model_pair.py'),
                                   '--project-root', str(self.project), '--role', 'executor', '--route', 'low'],
                                  capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(resolved.returncode, 0, resolved.stderr)
        self.assertEqual(json.loads(resolved.stdout)['thinking'], 'medium')
        ask = self.base / 'scoville-ask-for-codex/scoville-ask-for-codex/scripts/ask.py'
        request = {'operation': 'resolve', 'project_root': str(self.project),
                   'overrides': {'advisers': ['fable']}}
        resolved = subprocess.run([sys.executable, '-B', str(ask)], input=json.dumps(request),
                                  capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(resolved.returncode, 0, resolved.stderr)
        self.assertEqual(json.loads(resolved.stdout)['config']['claude']['timeout_seconds'], 2400)
        self.assertTrue(json.loads(resolved.stdout)['config']['pin_threads'])

    def test_rejected_patches_preserve_every_saved_byte(self):
        self.save({'workflow': {'context': {'worker_percent': 60}}, 'other': {'keep': True}})
        before = self.path.read_bytes()
        invalid = [ {'workflow': {key: {}}} for key in ('context', 'manager', 'pin_threads') ]
        invalid += [{'workflow': {'unknown': {}}}, {'ask': {'pin_threads': False}},
                    {'ask': {'claude': {'timeout_seconds': 0}}},
                    {'workflow': {'execute': {'low': {'reasoning': 'bad'}}}},
                    {'workflow': {'execute': {'low': {'model': False}}}}]
        for patch in invalid:
            with self.subTest(patch=patch):
                status, failed = self.run_setup('set', patch)
                self.assertNotEqual(status, 0)
                self.assertFalse(failed['ok'])
                self.assertTrue(failed['diagnostic'])
                self.assertEqual(self.path.read_bytes(), before)
        for raw in (b'', b'{\n"workflow":', b'\xff'):
            status, failed = self.run_setup('set', raw=raw)
            self.assertNotEqual(status, 0)
            self.assertFalse(failed['ok'])
            self.assertEqual(self.path.read_bytes(), before)
        status, saved = self.run_setup('set', {'workflow': {'execute': {'low': {'reasoning': 'high'}}}})
        self.assertEqual(status, 0, saved)
        self.assertNotIn('context', json.loads(self.path.read_text())['workflow'])

    def test_reasoning_limits_and_manual_values_remain(self):
        for level in ('none', 'minimal', 'max', 'ultra'):
            status, failed = self.run_setup('set', {'workflow': {'execute': {'low': {'reasoning': level}}}})
            self.assertNotEqual(status, 0)
            self.assertFalse(self.path.exists())
        for level in ('low', 'medium', 'high', 'xhigh'):
            status, saved = self.run_setup('set', {'workflow': {'execute': {'low': {'reasoning': level}}}})
            self.assertEqual(status, 0, saved)
        value = json.loads(self.path.read_text())
        value['workflow']['execute']['low']['reasoning'] = 'ultra'
        value['ask'] = {'presets': {'astra': {'effort': 'ultra'}}}
        self.save(value)
        status, saved = self.run_setup('set', {'ask': {'claude': {'timeout_seconds': 2400}}})
        self.assertEqual(status, 0, saved)
        self.assertEqual(saved['effective']['workflow']['execute']['low']['reasoning'], 'ultra')
        self.assertEqual(saved['effective']['ask']['presets']['astra']['effort'], 'ultra')

    def test_unknown_saved_workflow_key_does_not_become_ignored(self):
        self.save({'workflow': {'unknown': True}})
        before = self.path.read_bytes()
        status, failed = self.run_setup('show')
        self.assertNotEqual(status, 0)
        self.assertFalse(failed['ok'])
        self.assertEqual(self.path.read_bytes(), before)

    def test_explorer_override_is_saved_without_materializing_inherited_fields(self):
        self.save({'workflow': {'execute': {'low': {'model': 'gpt-6.1-sol', 'reasoning': 'high'}}}})
        status, saved = self.run_setup('set', {'workflow': {'explore': {'low': {'reasoning': 'medium'}}}})
        self.assertEqual(status, 0, saved)
        self.assertEqual(json.loads(self.path.read_text())['workflow']['explore'], {'low': {'reasoning': 'medium'}})
        self.assertEqual(saved['effective']['workflow']['explore']['low'], {'model': 'gpt-6.1-sol', 'reasoning': 'medium'})
        resolved = subprocess.run([sys.executable, '-B', str(self.workflow / 'resolve_model_pair.py'),
                                   '--project-root', str(self.project), '--role', 'explorer', '--route', 'low'],
                                  capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(resolved.returncode, 0, resolved.stderr)
        self.assertEqual(json.loads(resolved.stdout)['thinking'], 'medium')

    def test_setup_is_codex_suite_only(self):
        for profile, layout, expected in [('codex', 'suite', True), ('codex', 'standalone', False),
                                          ('general', 'suite', False)]:
            config = builder.load(ROOT, profile, layout)
            self.assertEqual(any(m['name'] == 'scoville-setup' for m in config['members']), expected)


if __name__ == '__main__':
    unittest.main()
