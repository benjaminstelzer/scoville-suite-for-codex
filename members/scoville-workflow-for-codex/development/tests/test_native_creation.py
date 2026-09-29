"""Real packaged builders consumed as native creation arguments."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_contract import PACKAGE, SUITE_ROOT

ID = '01a0e778-0c80-7660-b8b9-c8ce59a9fed4'


class NativeCreationTests(unittest.TestCase):
    def run_builder(self, script, *arguments):
        return subprocess.run([sys.executable, str(PACKAGE / 'scripts' / script), *map(str, arguments)],
                              env={**os.environ, 'CODEX_THREAD_ID': ID}, capture_output=True,
                              text=True, encoding='utf-8')

    def consume(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        # Tool schema boundary; real host acceptance is recorded separately.
        self.assertEqual(set(data), {'prompt', 'title', 'model', 'thinking', 'target'})
        self.assertEqual(data['target'], {'type': 'project', 'projectId': 'saved-project', 'environment': {'type': 'local'}})
        return data

    def test_dispatch_titles_cover_full_units_review_and_correction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            evidence = root / 'result.txt'
            evidence.write_text('completed: checked change; remaining work unchanged', encoding='utf-8')
            common = ['--project-root', root, '--format', 'create', '--project-id', 'saved-project',
                      '--project-name', 'Änderung 中文', '--worker-number', '7', '--model', 'gpt-6-sol', '--thinking', 'high']
            whole = self.consume(self.run_builder('build_dispatch_prompt.py', *common, '--unit', 'W-001', '--role', 'executor'))
            self.assertEqual(whole['title'], 'SC-WRK-7: Änderung 中文 · PLAN-0001/W-001/steps-1-2')
            for role, extra, label in [('executor', [], 'SC-WRK'), ('reviewer', ['--executor-result', evidence], 'SC-REV'),
                                       ('executor', ['--reviewer-result', evidence], 'SC-WRK')]:
                result = self.consume(self.run_builder('build_dispatch_prompt.py', *common, '--unit', 'W-001/step-1', '--role', role, *extra))
                self.assertEqual(result['title'], f'{label}-7: Änderung 中文 · PLAN-0001/W-001/step-1')
            invalid = self.run_builder('build_dispatch_prompt.py', *common, '--unit', 'W-001/step-1', '--role', 'reviewer')
            self.assertNotEqual(invalid.returncode, 0)
            self.assertEqual(invalid.stdout, '')
            self.assertIn('usage:', invalid.stderr)
            self.assertIn('--executor-result', invalid.stderr)

    def test_missing_create_arguments_have_actionable_diagnostics(self):
        result = self.run_builder('build_dispatch_prompt.py', '--project-root', PACKAGE,
                                  '--role', 'executor', '--unit', 'W-001', '--format', 'create')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        for parameter in ('--project-id', '--project-name', '--model', '--thinking'):
            self.assertIn(parameter, result.stderr)
        self.assertIn('usage:', result.stderr)

    def test_manager_uses_own_native_pair_and_preserves_handoff(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); handoff = root / 'handoff.md'; rollout = root / 'rollout.jsonl'
            body = 'Pending question: deploy? Unanswered; source chat retained.\nWorker uses gpt-6-astra/medium. Completed Step 1. Stop before deployment.'
            handoff.write_text(body, encoding='utf-8')
            events = [{'ordinal': 1, 'type': 'session_meta', 'payload': {'session_id': ID}},
                      {'ordinal': 2, 'type': 'turn_context', 'payload': {'model': 'gpt-6-sol', 'effort': 'high'}}]
            def save(): rollout.write_text('\n'.join(json.dumps(e) for e in events), encoding='utf-8')
            save()
            args = ['--project-id', 'saved-project', '--project-name', 'Example', '--plan-id', 'PLAN-0001',
                    '--manager-number', '8', '--handoff-file', handoff, '--rollout', rollout]
            data = self.consume(self.run_builder('build_manager_handoff.py', *args))
            self.assertEqual((data['model'], data['thinking']), ('gpt-6-sol', 'high'))
            self.assertEqual(data['title'], 'SC-MGR-8: Example · PLAN-0001')
            self.assertIn(body, data['prompt'])
            self.assertIn(ID, data['prompt'])
            self.assertTrue(data['prompt'].startswith('FIRST ACTION'))
            self.assertLess(data['prompt'].index('send_message_to_thread'), data['prompt'].index('SKILL.md'))
            self.assertEqual(data['prompt'].count('I have the information.'), 1)
            self.assertIn('already consumed the checkpoint boundary', data['prompt'])
            routed = self.consume(self.run_builder('build_manager_handoff.py', *args, '--report-to-thread-id', ID))
            self.assertIn(f'Final report destination: {ID}.', routed['prompt'])
            invalid_id = self.run_builder('build_manager_handoff.py', *args, '--report-to-thread-id', '01a0e778-0c80-7660-b8b9-c8ce9a9fed4')
            self.assertNotEqual(invalid_id.returncode, 0)
            self.assertEqual(invalid_id.stdout, '')
            self.assertIn('--report-to-thread-id must be', invalid_id.stderr)
            self.assertIn('usage:', invalid_id.stderr)
            override = self.consume(self.run_builder('build_manager_handoff.py', *args, '--override-model', 'gpt-6-astra', '--override-thinking', 'high'))
            self.assertEqual(override['model'], 'gpt-6-astra')
            for mutation in ('missing_pair', 'wrong_identity', 'empty_handoff'):
                if mutation == 'missing_pair': events[-1]['payload'].pop('effort')
                elif mutation == 'wrong_identity':
                    events[-1]['payload']['effort'] = 'high'; events[0]['payload']['session_id'] = 'wrong'
                else:
                    events[0]['payload']['session_id'] = ID; handoff.write_text('', encoding='utf-8')
                save()
                result = self.run_builder('build_manager_handoff.py', *args)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, '')


if __name__ == '__main__':
    unittest.main()
