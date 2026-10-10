"""Run the diagnostic's unchanged correction through the target shell."""
import json
import os
from pathlib import Path
import shutil
import shlex
import subprocess
import sys
import tempfile
import unittest

from test_contract import PACKAGE, SUITE_ROOT
from native_task_arguments import budget_retry, shell_command


class BudgetRetryTests(unittest.TestCase):
    def test_dispatch_corrections_preserve_literal_arguments(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project ü ' $()"
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            plan = root / 'docs/plans/0001-validate-profile.md'
            text = plan.read_text(encoding='utf-8').replace('1. Read the canonical files.', '1. [status: in_progress] Read the canonical files.').replace('2. Check the local record shapes.', '2. [status: todo] Check the local record shapes.')
            text = text.replace('Steps:\n', 'Instructions: ' + 'Retain the authorized scope. ' * 40 + '\nSteps:\n', 1)
            plan.write_text(text, encoding='utf-8', newline='\n')
            assignment = root / "assignment ü ' $().txt"
            project = 'Fixture "quoted" ü \' $() \\"tail'
            commands = [
                ('build_dispatch_prompt.py', ['--project-root', str(root), '--unit', 'W-001/step-1',
                 '--role', 'executor', '--format', 'create', '--manager-agent-id', '/root/manager',
                 '--project-name', project, '--worker-number', '1', '--model', 'gpt-6-sol',
                 '--thinking', 'high', '--assignment-file', str(assignment), '--max-output-bytes=512'])]
            for name, args in commands:
                with self.subTest(helper=name):
                    failed = subprocess.run([sys.executable, str(PACKAGE / 'scripts' / name), *args],
                                            capture_output=True, text=True, encoding='utf-8')
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertEqual(failed.stdout, '')
                    self.assertIn('OUTPUT_BUDGET_EXCEEDED', failed.stderr)
                    if name == 'build_dispatch_prompt.py':
                        self.assertFalse(assignment.exists())
                    prefix = '& {' if os.name == 'nt' else shlex.quote(sys.executable) + ' '
                    commands = [line for line in failed.stderr.splitlines() if line.startswith(prefix)]
                    self.assertEqual(len(commands), 1)
                    correction = commands[0]
                    self.assertEqual(correction.count('--max-output-bytes'), 1)
                    shell = ['powershell', '-NoProfile', '-NonInteractive', '-Command'] if os.name == 'nt' else ['sh', '-c']
                    corrected = subprocess.run([*shell, correction], capture_output=True, text=True, encoding='utf-8')
                    self.assertEqual(corrected.returncode, 0, corrected.stderr)
                    payload = json.loads(corrected.stdout)
                    if name == 'build_dispatch_prompt.py':
                        self.assertEqual(set(payload), {'task_name', 'message', 'fork_turns', 'model', 'reasoning_effort'})
                        self.assertIn(str(assignment), payload['message'])
                        self.assertIn(project, assignment.read_text(encoding='utf-8'))
                        self.assertEqual(payload['model'], 'gpt-6-sol')

    def test_shell_preserves_quotes_backslashes_empty_arguments_and_exit_code(self):
        values = ['"quoted"', 'slash\\"quote', 'two\\\\"quote', 'space tail\\', '', "a'b", '$()']
        command = shell_command([sys.executable, '-c', 'import sys,json;print(json.dumps(sys.argv[1:]))', *values])
        shell = ['powershell', '-NoProfile', '-NonInteractive', '-Command'] if os.name == 'nt' else ['sh', '-c']
        result = subprocess.run([*shell, command], capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), values)
        failed = subprocess.run([*shell, shell_command([sys.executable, '-c', 'import sys;sys.exit(7)'])],
                                capture_output=True, text=True)
        self.assertEqual(failed.returncode, 7)

    def test_unrelated_or_invalid_diagnostics_have_no_retry(self):
        for value in ('not json', '[]', '{}', '{"diagnostics":null}',
                      json.dumps({'diagnostics': [{'code': 'OUTPUT_BUDGET_EXCEEDED', 'observed': {'required_bytes': True}}]})):
            self.assertEqual(budget_retry(value, ['python', 'helper.py']), '')


if __name__ == '__main__':
    unittest.main()
