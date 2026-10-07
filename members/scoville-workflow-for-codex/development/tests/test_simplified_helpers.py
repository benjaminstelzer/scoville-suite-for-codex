"""Packaged route and saved-position integration; native dispatch is tested live."""
import json
import hashlib
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

from test_contract import PACKAGE, SUITE_ROOT


class SimplifiedHelpersTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'project'
        shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', self.root)
        self.plan = self.root / 'docs/plans/0001-validate-profile.md'
        self.original = self.plan.read_text(encoding='utf-8')
        self.scope = self.root / 'scope.txt'
        self.scope.write_text('Auftrag erhalten: Text prüfen.', encoding='utf-8')
        self.result = self.root / 'result.txt'
        self.result.write_text('completed: original effects retained', encoding='utf-8')
        self.config = self.root / '.scoville/config.json'
        self.config.parent.mkdir()
        self.config.write_text(json.dumps({'workflow': {
            'execute': {'medium': {'model': 'gpt-6-luna', 'reasoning': 'medium'}},
            'review': {'medium': {'model': 'gpt-6-sol', 'reasoning': 'high'}}}}), encoding='utf-8')

    def cli(self, name, *args, error=None):
        result = subprocess.run([sys.executable, '-B', str(PACKAGE / 'scripts' / name), *map(str, args)],
                                capture_output=True, text=True, encoding='utf-8')
        if error:
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, '')
            self.assertIn(error, result.stderr)
            return
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def dispatch(self, *args, role='executor', error=None):
        if not any(flag in args for flag in ('--assignment-file', '--context-handoff', '--predecessor-agent-id')):
            args = (*args, '--assignment-file', self.root / f'assignment-{uuid.uuid4().hex}.txt')
        return self.cli('build_dispatch_prompt.py', '--project-root', self.root,
                        '--unit', 'W-001/step-1', '--role', role, '--format', 'create',
                        '--manager-agent-id', '/root/manager', '--project-name', 'test',
                        '--worker-number', '1', *args, error=error)

    def test_routes_overrides_and_retained_pairs(self):
        self.dispatch(error='--route CLASS or both --model and --thinking')
        actual = self.dispatch('--route', 'medium')
        self.assertEqual((actual['model'], actual['reasoning_effort']), ('gpt-6-luna', 'medium'))
        reviewed = self.dispatch('--route', 'medium', '--executor-result', self.result, '--supplemental-context', self.scope, role='reviewer')
        self.assertEqual((reviewed['model'], reviewed['reasoning_effort']), ('gpt-6-sol', 'high'))
        for overrides, pair in [(['--model', 'gpt-6-astra'], ('gpt-6-astra', 'medium')),
                                (['--thinking', 'high'], ('gpt-6-luna', 'high'))]:
            result = self.dispatch('--route', 'medium', *overrides)
            self.assertEqual((result['model'], result['reasoning_effort']), pair)
        # Configuration changes cannot change a correction or recovery pair.
        self.config.write_text('{invalid', encoding='utf-8')
        for extra in [[], ['--reviewer-result', self.result],
                      ['--context-handoff', self.result, '--supplemental-context', self.scope,
                       '--predecessor-agent-id', '/root/previous']]:
            if extra:
                self.dispatch('--route', 'medium', *extra, error='original launched pair')
            output = self.dispatch('--model', actual['model'], '--thinking', actual['reasoning_effort'], *extra)
            self.assertEqual((output['model'], output['reasoning_effort']), ('gpt-6-luna', 'medium'))
            self.assertEqual(set(output), {'task_name', 'message', 'fork_turns', 'model', 'reasoning_effort'})

    def test_assignment_delivery_tools_reach_actual_complete_file_consumer(self):
        payload = self.root / 'complete Grüße 中文.txt'
        payload.write_text('completed: full result\nRequired final fact: Grüße 中文.\n', encoding='utf-8')
        cases = [
            ('executor', ['--route', 'medium']),
            ('reviewer', ['--route', 'medium', '--executor-result', self.result, '--supplemental-context', self.scope]),
            ('executor', ['--model', 'gpt-6-luna', '--thinking', 'medium', '--reviewer-result', self.result]),
            ('executor', ['--model', 'gpt-6-luna', '--thinking', 'medium', '--context-handoff', self.result,
                          '--supplemental-context', self.scope, '--predecessor-agent-id', '/root/previous']),
        ]
        for role, extra in cases:
            with self.subTest(role=role, extra=extra):
                assignment = self.root / f'delivery-{uuid.uuid4().hex}.txt'
                carrier = self.dispatch(*extra, '--assignment-file', assignment, role=role)
                self.assertIn(str(assignment), carrier['message'])
                fields = dict(line.split(': ', 1) for line in assignment.read_text(encoding='utf-8').splitlines()
                              if line.startswith(('text_size_checker: ', 'python: ')))
                self.assertEqual(fields['python'], sys.executable)
                self.assertEqual(Path(fields['text_size_checker']), (PACKAGE / 'scripts/check_text_size.py').resolve())
                consumed = subprocess.run([fields['python'], fields['text_size_checker'], '--file', str(payload),
                                           '--publish-full', '--project-root', str(self.root)],
                                          capture_output=True, text=True, encoding='utf-8')
                self.assertEqual(consumed.returncode, 0, consumed.stderr)
                metadata = json.loads(consumed.stdout)
                received = Path(metadata['full_file']).read_bytes()
                self.assertEqual(received, payload.read_bytes())
                self.assertEqual(hashlib.sha256(received).hexdigest(), metadata['sha256'])
                self.assertEqual(metadata['status'], 'complete_file')
                self.assertNotIn('tool_output_limit_tokens', metadata)

    def test_missing_delivery_checker_prevents_assignment_then_restoration_succeeds(self):
        suite = Path(self.temp.name) / 'copied suite'
        copy = suite / PACKAGE.name
        shutil.copytree(PACKAGE, copy)
        shutil.copytree(PACKAGE.parent / 'scoville-code', suite / 'scoville-code')
        checker = copy / 'scripts/check_text_size.py'
        original = checker.read_bytes()
        checker.unlink()
        assignment = self.root / 'restored-checker-assignment.txt'
        command = [sys.executable, '-B', str(copy / 'scripts/build_dispatch_prompt.py'),
                   '--project-root', str(self.root), '--unit', 'W-001/step-1', '--role', 'executor',
                   '--format', 'create', '--manager-agent-id', '/root/manager', '--project-name', 'test',
                   '--worker-number', '1', '--route', 'medium', '--assignment-file', str(assignment)]
        failed = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(failed.stdout, '')
        self.assertIn(str(checker.resolve()), failed.stderr)
        self.assertIn('intact matching Workflow package', failed.stderr)
        self.assertFalse(assignment.exists())
        checker.write_bytes(original)
        corrected = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(corrected.returncode, 0, corrected.stderr)
        self.assertIn(str(assignment), json.loads(corrected.stdout)['message'])
        self.assertIn(str(checker.resolve()), assignment.read_text(encoding='utf-8'))

    def saved_steps(self, steps):
        self.plan.write_text(self.original.replace('1. Read the canonical files.\n2. Check the local record shapes.', steps), encoding='utf-8')

    def progress(self, error=None):
        return self.cli('run_feedback.py', 'progress', '--project-root', self.root,
                        '--project', 'test', error=error)

    def test_saved_start_diagnostics_and_corrected_display(self):
        self.progress(error='unmarked Steps')
        self.saved_steps('1. [status: todo] First.\n2. [status: todo] Second.')
        self.progress(error='found 0')
        self.saved_steps('1. [status: in_progress] First.\n2. [status: todo] Second.\n3. [status: in_progress] Third.')
        self.progress(error='found 2')
        for steps, point in [('1. [status: in_progress] First.\n2. [status: in_progress] Second.', 'W-001/steps-1-2'),
                             ('1. [status: done] First.\n2. [status: in_progress] Second.', 'W-001/step-2')]:
            self.saved_steps(steps)
            before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
            generated = self.progress()
            # The existing explicit display consumer must produce identical output.
            expected = self.cli('run_feedback.py', 'progress', '--project', 'test', '--plan', 'PLAN-0001',
                                '--point', point)
            self.assertEqual(generated, expected)
            self.assertEqual(generated['message'].split('\n', 1)[1], generated['text'])
            self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        self.plan.write_text(self.plan.read_text(encoding='utf-8').replace('Status: in_progress', 'Status: paused', 1), encoding='utf-8')
        self.progress(error='no started current Work Item')
        self.plan.write_text(self.original.replace('Steps:\n1. Read the canonical files.\n2. Check the local record shapes.\n', ''), encoding='utf-8')
        self.assertIn('PLAN-0001 → W-001**', self.progress()['text'])

    def test_large_progress_budget_and_corrected_runner_message(self):
        self.saved_steps('1. [status: in_progress] First.\n2. [status: todo] Second.')
        self.plan.write_text(self.plan.read_text(encoding='utf-8').replace(
            'Steps:\n', 'Instructions: ' + 'é' * 40_000 + '\nSteps:\n', 1), encoding='utf-8')
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        base = ['progress', '--project-root', self.root, '--project', 'test']
        self.cli('run_feedback.py', *base, error='OUTPUT_BUDGET_EXCEEDED')
        self.cli('run_feedback.py', *base, '--max-output-bytes', '0', error='OUTPUT_BUDGET_INVALID')
        generated = self.cli('run_feedback.py', *base, '--max-output-bytes', '131072')
        expected = self.cli('run_feedback.py', 'progress', '--project', 'test',
                            '--plan', 'PLAN-0001', '--point', 'W-001/step-1')
        self.assertEqual(generated, expected)
        self.assertEqual(generated['message'].split('\n', 1)[1], generated['text'])
        self.cli('run_feedback.py', 'progress', '--project', 'test', '--plan', 'PLAN-0001',
                 '--point', 'W-001/step-1', '--max-output-bytes', '131072',
                 error='--max-output-bytes requires --project-root')
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_explicit_progress_preserves_historical_groups_and_rejects_unstarted_scope(self):
        self.saved_steps('1. [status: in_progress] First.\n2. [status: done] Second.\n'
                         '3. [status: in_progress] Third.\n4. [status: in_progress] Fourth.\n'
                         '5. [status: todo] Fifth.\n6. [status: cancelled] Sixth.')
        before = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        base = ['progress', '--project-root', self.root, '--project', 'test']
        self.cli('run_feedback.py', *base, error='Supply --point')
        for point in ('W-001/step-1', 'W-001/step-3', 'W-001/steps-3-4'):
            actual = self.cli('run_feedback.py', *base, '--point', point)
            expected = self.cli('run_feedback.py', 'progress', '--project', 'test',
                                '--plan', 'PLAN-0001', '--point', point)
            self.assertEqual(actual, expected)
        for point in ('W-001/step-2', 'W-001/steps-1-3', 'W-001/step-5',
                      'W-001/step-6', 'W-001/step-9'):
            self.cli('run_feedback.py', *base, '--point', point, error='only saved in_progress')
        for point, error in [('W-002/step-1', 'saved current Work Item'),
                             ('W-001', 'item with Steps'), ('W-001/steps-4-3', 'ascending')]:
            self.cli('run_feedback.py', *base, '--point', point, error=error)
        self.assertEqual(before, {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
        self.saved_steps('1. [status: in_progress] First.\n2. Unknown.')
        self.cli('run_feedback.py', *base, '--point', 'W-001/step-1', error='unmarked Steps')
        self.plan.write_text(self.original.replace('Steps:\n1. Read the canonical files.\n2. Check the local record shapes.\n', ''), encoding='utf-8')
        actual = self.cli('run_feedback.py', *base, '--point', 'W-001')
        self.assertEqual(actual, self.progress())
