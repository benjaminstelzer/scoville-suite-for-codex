"""Consume the packaged CLI in manager startup, issue recovery and final display."""
import importlib.util
import base64
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_contract import PACKAGE

SCRIPT = PACKAGE / 'scripts/run_feedback.py'
spec = importlib.util.spec_from_file_location('packaged_feedback', SCRIPT)
feedback = importlib.util.module_from_spec(spec)
spec.loader.exec_module(feedback)


class RunFeedbackTests(unittest.TestCase):
    def test_report_decode_failures_then_each_corrected_consumer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project Ä 中文'
            root.mkdir()
            body = self.text(root, 'Actual retained question Ä 中文.')
            resolution = self.text(root, 'Known answer Ä 中文.', 'answer.txt')
            for command in ('read', 'finish', 'complete', 'add', 'resolve'):
                with self.subTest(command=command):
                    report = self.create(root)
                    initial = self.cli('add', '--report-file', report, '--kind', 'question',
                                       '--location', 'Startup', '--text-file', body)
                    known = report.read_bytes()
                    arguments = [command, '--report-file', report]
                    if command == 'finish':
                        arguments += ['--completed']
                    elif command == 'complete':
                        arguments += ['--completed', '--project', 'Fixture', '--plan', 'PLAN-0035',
                                      '--point', 'W-017', '--text', 'Completed actual scope.']
                    elif command == 'add':
                        arguments += ['--kind', 'problem', '--location', 'Startup', '--text-file', body]
                    elif command == 'resolve':
                        arguments += ['--issue-id', initial['issue_id'], '--text-file', resolution]
                    damaged = known + b'\xff'
                    report.write_bytes(damaged)
                    failed = self.cli(*arguments, success=False)
                    self.assertIn('--report-file', failed.stderr)
                    self.assertIn(str(report), failed.stderr)
                    self.assertIn('UTF-8', failed.stderr)
                    self.assertEqual(report.read_bytes(), damaged)
                    report.write_bytes(known)
                    received = self.cli(*arguments)
                    displayed = self.cli('read', '--report-file', report)
                    self.assertIn('Actual retained question Ä 中文.', displayed['display_text'])
                    self.assertEqual(displayed['text'], report.read_bytes().decode('utf-8'))
                    if command == 'complete':
                        self.assertEqual(received['report_text'], displayed['text'])
                    if command == 'resolve':
                        self.assertIn('Known answer Ä 中文.', displayed['display_text'])
                    if command in ('read', 'finish', 'complete'):
                        self.assertEqual(report.read_bytes(), known)

    def test_missing_project_and_report_paths_then_corrected_consumer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project Ä 中文'
            failed = self.cli('create', '--project-root', root, success=False)
            self.assertIn('--project-root', failed.stderr)
            self.assertIn(str(root), failed.stderr)
            self.assertFalse(root.exists())
            root.mkdir()
            missing = root / 'absent' / '.scoville' / ('workflow-run-20260101T000000Z-' + '0' * 32 + '.md')
            failed = self.cli('read', '--report-file', missing, success=False)
            self.assertIn('--report-file', failed.stderr)
            self.assertIn(str(missing), failed.stderr)
            self.assertFalse(missing.parent.exists())
            report = self.create(root)
            received = self.cli('read', '--report-file', report)
            self.assertEqual(Path(received['report_file']), report)
            self.assertEqual(received['text'], '')
            self.assertEqual(report.read_bytes(), b'')

    def test_body_file_failures_then_each_actual_consumer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project Ä 中文'
            root.mkdir()
            body = 'Actual apostrophe\'s "diagnostic" Ä 中文, `literal` and $(not-a-command).\nRetain exact\\path.'
            quoted = '\n'.join('> ' + line for line in body.splitlines())
            for command in ('status', 'complete', 'add', 'resolve'):
                with self.subTest(command=command):
                    source = root / (command + ' Ä 中文.txt')
                    report = self.create(root)
                    if command == 'status':
                        arguments = ['status', '--kind', 'blocked', '--project', 'Fixture']
                    elif command == 'complete':
                        arguments = ['complete', '--report-file', report, '--completed', '--project', 'Fixture',
                                     '--plan', 'PLAN-0035', '--point', 'W-001']
                    elif command == 'add':
                        arguments = ['add', '--report-file', report, '--kind', 'question', '--location', 'Startup']
                    else:
                        question = self.text(root, 'Actual retained question.', 'initial-question.txt')
                        issue = self.cli('add', '--report-file', report, '--kind', 'question',
                                         '--location', 'Startup', '--text-file', question)
                        arguments = ['resolve', '--report-file', report, '--issue-id', issue['issue_id']]
                    before = report.read_bytes()
                    for invalid in (None, b'\xff'):
                        if invalid is not None:
                            source.write_bytes(invalid)
                        failed = self.cli(*arguments, '--text-file', source, success=False)
                        self.assertIn('Invalid argument --text-file', failed.stderr)
                        self.assertIn(str(source), failed.stderr)
                        self.assertIn('existing readable UTF-8 file', failed.stderr)
                        self.assertEqual(report.read_bytes(), before)
                    source.write_text(body, encoding='utf-8', newline='\n')
                    self.assertEqual(source.read_bytes(), body.encode('utf-8'))
                    result = self.cli(*arguments, '--text-file', source)
                    if command in ('status', 'complete'):
                        received = result['message'].split('\n', 1)[1]
                        self.assertEqual(received, result['text'])
                        self.assertEqual(received.split('\n\n', 1)[1], body)
                        if command == 'complete':
                            self.assertEqual(self.cli('read', '--report-file', report)['text'], feedback.CLEAN)
                        else:
                            self.assertEqual(report.read_bytes(), before)
                    else:
                        received = self.cli('read', '--report-file', result['report_file'])
                        self.assertIn(quoted, received['text'])
                        self.assertIn(quoted, received['display_text'])

    def test_write_prohibited_status_uses_documented_runtime_encoder_and_host_shell(self):
        instructions = (PACKAGE / 'references/run-feedback.md').read_text(encoding='utf-8')
        encoders = [block for block in re.findall(r'```javascript\n(.*?)\n```', instructions, re.S)
                    if 'function statusBodyBase64(' in block]
        self.assertEqual(len(encoders), 1)
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Actions needs Node only to exercise the standard ECMAScript runtime encoder')
        shells = [shutil.which(name) for name in ('powershell', 'pwsh')] if os.name == 'nt' else [shutil.which('sh')]
        shells = list(dict.fromkeys(shell for shell in shells if shell))
        self.assertTrue(shells, 'The documented write-prohibited command needs an actual host shell')
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / 'must-not-exist.txt'
            embedded = ("$(New-Item -ItemType File -Path '" + str(marker) + "')" if os.name == 'nt'
                        else "$(touch '" + str(marker) + "')")
            body = 'Actual apostrophe\'s "quoted" Ä 中文; `literal` ' + embedded + '\nKeep exact\\path.'
            code = ("const vm=require('node:vm'); const input=JSON.parse(process.argv[1]); "
                    "const context=vm.createContext({body:input.body,Buffer:undefined,btoa:undefined,TextEncoder:undefined}); "
                    "vm.runInContext(input.encoder,context); "
                    "process.stdout.write(vm.runInContext('statusBodyBase64(body)',context));")
            generated = subprocess.run([node, '-e', code, json.dumps({'encoder': encoders[0], 'body': body}, ensure_ascii=False)],
                                       capture_output=True, text=True, encoding='utf-8', timeout=30)
            self.assertEqual(generated.returncode, 0, generated.stderr)
            encoded = generated.stdout
            self.assertEqual(encoded, base64.b64encode(body.encode('utf-8')).decode('ascii'))
            argv = [sys.executable, '-B', str(SCRIPT), 'status', '--kind', 'blocked',
                    '--project', 'Fixture', '--text-base64', encoded]
            command = ('& ' + ' '.join("'" + value.replace("'", "''") + "'" for value in argv)
                       if os.name == 'nt' else shlex.join(argv))
            for invalid in ('not-base64!', '/w=='):
                failed = self.cli('status', '--kind', 'blocked', '--project', 'Fixture',
                                  '--text-base64', invalid, success=False)
                self.assertIn('Invalid argument --text-base64', failed.stderr)
                self.assertIn('UTF-8', failed.stderr)
                self.assertIn('standard Base64', failed.stderr)
            corrected = self.cli(*argv[3:])
            self.assertEqual(corrected['text'].split('\n\n', 1)[1], body)
            for shell in shells:
                with self.subTest(shell=shell):
                    invocation = ([shell, '-NoProfile', '-NonInteractive', '-Command', command]
                                  if os.name == 'nt' else [shell, '-c', command])
                    result = subprocess.run(invocation, capture_output=True, text=True, encoding='utf-8', timeout=30)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    received = json.loads(result.stdout)
                    self.assertEqual(received['message'].split('\n', 1)[1], received['text'])
                    self.assertEqual(received['text'].split('\n\n', 1)[1], body)
                    self.assertFalse(marker.exists(), 'Body content must not run as shell code')

    def cli(self, *args, success=True):
        result = subprocess.run([sys.executable, '-B', str(SCRIPT), *map(str, args)],
                                capture_output=True, text=True, encoding='utf-8')
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        self.assertIn('usage:', result.stderr)
        return result

    def create(self, root):
        return Path(self.cli('create', '--project-root', root)['report_file'])

    def text(self, root, contents, name='issue.txt'):
        path = root / name
        path.write_text(contents, encoding='utf-8', newline='\n')
        return path

    def test_unique_empty_files_then_clean_completion_and_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first, second = self.create(root), self.create(root)
            self.assertNotEqual(first, second)
            self.assertEqual(first.parent, root.resolve() / '.scoville')
            self.assertTrue(first.is_absolute())
            self.assertEqual(first.read_bytes(), b'')
            self.assertEqual(second.read_bytes(), b'')
            result = self.cli('finish', '--report-file', first, '--completed')
            # The actual runner's read consumer receives the complete file text.
            received = self.cli('read', '--report-file', result['report_file'])
            self.assertEqual(received['text'], feedback.CLEAN)
            self.assertEqual(received['display_text'], feedback.CLEAN)
            self.assertEqual(first.read_bytes(), feedback.CLEAN.encode('utf-8'))
            self.assertEqual(self.cli('finish', '--report-file', first, '--completed'), received)
            self.assertEqual(second.read_bytes(), b'')

    def test_complete_prepares_message_before_report_and_repeats_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = self.create(root)
            base = ['complete', '--report-file', report, '--completed', '--project', 'Täst 中文',
                    '--plan', 'PLAN-0035', '--point', 'W-001/steps-1-2']
            failed = self.cli(*base, '--text', ' ', success=False)
            self.assertIn('nonempty text', failed.stderr)
            self.assertEqual(report.read_bytes(), b'')
            self.cli(*base, '--text-file', root / 'missing.txt', success=False)
            self.assertEqual(report.read_bytes(), b'')
            self.cli(*base[:-1], 'bad-point', '--text', 'Completed scope.', success=False)
            self.assertEqual(report.read_bytes(), b'')
            self.cli(*base[0:3], *base[4:], '--text', 'Completed scope.', success=False)
            self.assertEqual(report.read_bytes(), b'')
            received = self.cli(*base, '--text', 'Completed scope.')
            control, displayed = received['message'].split('\n', 1)
            self.assertEqual(control, 'COMPLETED')
            self.assertEqual(displayed, received['text'])
            self.assertEqual(received['report_text'], feedback.CLEAN)
            self.assertEqual(self.cli('read', '--report-file', received['report_file'])['display_text'], feedback.CLEAN)
            before = report.stat().st_mtime_ns
            self.assertEqual(self.cli(*base, '--text', 'Completed scope.'), received)
            self.assertEqual(report.stat().st_mtime_ns, before)
            self.assertEqual(report.read_bytes(), feedback.CLEAN.encode('utf-8'))

    def test_complete_preserves_documented_problems_and_save_failure_has_no_message(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = self.create(root)
            body = self.text(root, 'Nonblocking problem retained for user inspection.')
            issue = self.cli('add', '--report-file', report, '--kind', 'problem',
                             '--location', 'PLAN-0035 / W-001', '--text-file', body)
            answer = self.text(root, 'User reviewed it; requested scope can close.', 'answer.txt')
            self.cli('resolve', '--report-file', report, '--issue-id', issue['issue_id'], '--text-file', answer)
            before = report.read_bytes()
            args = ['complete', '--report-file', report, '--completed', '--project', 'Fixture',
                    '--plan', 'PLAN-0035', '--point', 'W-001', '--text', 'Scope passed acceptance.']
            received = self.cli(*args)
            self.assertEqual(report.read_bytes(), before)
            self.assertEqual(received['report_text'], before.decode('utf-8'))
            self.assertNotIn('scoville-issue:', received['display_text'])
            self.assertIn('Nonblocking problem', received['display_text'])
            self.assertEqual(self.cli(*args), received)
            empty = self.create(root)
            with patch.object(feedback, 'save', side_effect=OSError('disk full')):
                with self.assertRaisesRegex(OSError, 'disk full'):
                    feedback.complete_report(empty, 'Fixture', 'PLAN-0035', 'W-001', 'Scope accepted.')
            self.assertEqual(empty.read_bytes(), b'')

    def test_complete_output_failure_restores_report_and_preserves_concurrent_edit(self):
        from unittest.mock import patch
        import io
        with tempfile.TemporaryDirectory() as directory:
            report = self.create(Path(directory))
            argv = ['run_feedback.py', 'complete', '--report-file', str(report), '--completed',
                    '--project', 'Fixture', '--plan', 'PLAN-0035', '--point', 'W-001', '--text', 'Scope accepted.']
            class FailingOutput(io.StringIO):
                def write(self, value):
                    raise OSError('simulated stdout write failure')
            with patch.object(sys, 'argv', argv), patch.object(sys, 'stdout', FailingOutput()), \
                 patch.object(sys, 'stderr', io.StringIO()), patch.object(feedback, 'configure_utf8'):
                with self.assertRaises(SystemExit) as failed:
                    feedback.main()
                self.assertEqual(failed.exception.code, 2)
                self.assertEqual(sys.stdout.getvalue(), '')
                self.assertIn('simulated stdout write failure', sys.stderr.getvalue())
            self.assertEqual(report.read_bytes(), b'')
            for exception in (ValueError('I/O operation on closed file'), OSError('flush failed')):
                def fail_delivery(payload):
                    raise exception
                with self.assertRaises(type(exception)):
                    feedback.complete_report(report, 'Fixture', 'PLAN-0035', 'W-001', 'Scope accepted.', fail_delivery)
                self.assertEqual(report.read_bytes(), b'')
            class FailingFlush(io.StringIO):
                def flush(self):
                    raise OSError('simulated stdout flush failure')
            with patch.object(sys, 'argv', argv), patch.object(sys, 'stdout', FailingFlush()), \
                 patch.object(sys, 'stderr', io.StringIO()), patch.object(feedback, 'configure_utf8'):
                with self.assertRaises(SystemExit) as failed:
                    feedback.main()
                self.assertEqual(failed.exception.code, 2)
                self.assertIn('simulated stdout flush failure', sys.stderr.getvalue())
            self.assertEqual(report.read_bytes(), b'')
            def concurrent_output(payload):
                report.write_text('Concurrent note.\n', encoding='utf-8', newline='\n')
                raise OSError('failed delivery')
            with self.assertRaisesRegex(ValueError, 'rollback failed'):
                feedback.complete_report(report, 'Fixture', 'PLAN-0035', 'W-001', 'Scope accepted.', concurrent_output)
            self.assertEqual(report.read_bytes(), b'Concurrent note.\n')
            clean = self.create(Path(directory))
            with self.assertRaises(UnicodeError):
                feedback.complete_report(clean, 'Fixture', 'PLAN-0035', 'W-001', '\ud800')
            self.assertEqual(clean.read_bytes(), b'')

    def test_complete_preserves_open_nonblocking_documented_problem(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = self.create(root)
            body = self.text(root, 'Nonblocking historical issue; requested acceptance is met.')
            self.cli('add', '--report-file', report, '--kind', 'problem', '--location', 'PLAN-0035 / W-001', '--text-file', body)
            before = report.read_bytes()
            result = self.cli('complete', '--report-file', report, '--completed', '--project', 'Fixture',
                              '--plan', 'PLAN-0035', '--point', 'W-001', '--text', 'Requested scope accepted; retained issue is nonblocking.')
            self.assertEqual(report.read_bytes(), before)
            self.assertIn('Status: Open', result['display_text'])
            self.assertEqual(result['report_text'], before.decode('utf-8'))

    def test_project_plan_point_changes_only_without_scope_body(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = self.create(root)
            scope = self.text(root, 'Finishing PLAN-0025, W-003 step-1 to step-4.\nNo commits.', 'scope.txt')
            previous = None
            displayed = []
            for project, plan, point in [('Täst 中文', 'PLAN-0025', 'W-003/step-1'),
                                          ('Täst 中文', 'PLAN-0025', 'W-003/step-1'),
                                          ('Täst 中文', 'PLAN-0025', 'W-003/step-2'),
                                          ('Täst 中文', 'PLAN-0026', 'W-003/step-2'),
                                          ('Next project', 'PLAN-0026', 'W-003/step-2')]:
                args = ['progress', '--project', project, '--plan', plan, '--point', point, '--scope-file', scope]
                if previous:
                    args.extend(['--previous-key', previous])
                received = self.cli(*args)
                self.assertEqual(received['message'], f"WORKING_ON {received['key']}\n{received['text']}" if received['changed'] else '')
                if received['changed']:
                    displayed.append(received['text'])
                else:
                    self.assertEqual(received['text'], '')
                previous = received['key']
            self.assertEqual(len(displayed), 4)
            self.assertEqual(displayed[0], '**Working on: Täst 中文 → PLAN-0025 → W-003/step-1**')
            scope.unlink()
            # Legacy callers need no scope file, and new callers omit it entirely.
            self.assertEqual(self.cli('progress', '--project', 'test', '--plan', 'PLAN-0001', '--point', 'W-001'),
                             self.cli('progress', '--project', 'test', '--plan', 'PLAN-0001', '--point', 'W-001', '--scope-file', scope))
            scope.write_text('New authorized scope, same point.', encoding='utf-8')
            received = self.cli('progress', '--project', 'Next project', '--plan', 'PLAN-0026',
                                '--point', 'W-003/step-2', '--scope-file', scope, '--previous-key', previous)
            self.assertFalse(received['changed'])
            self.assertEqual(report.read_bytes(), b'')

    def test_status_payloads_are_ready_for_runner_display_without_rewriting(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            body = self.text(root, 'Welche Adresse soll verwendet werden?\nDer Export wartet auf deine Antwort.')
            for kind, label, control in [('decision', 'Decision needed', 'NEEDS_USER_DECISION'),
                                         ('blocked', 'Blocked', 'BLOCKED'), ('paused', 'Paused', 'STOPPED'),
                                         ('completed', 'Completed', 'COMPLETED')]:
                received = self.cli('status', '--kind', kind, '--project', 'test',
                                    '--plan', 'PLAN-0007', '--point', 'W-001/step-1', '--text-file', body)
                received_control, displayed = received['message'].split('\n', 1)
                self.assertEqual(received_control, control)
                self.assertEqual(displayed, received['text'])
                self.assertEqual(displayed.split('\n\n', 1)[0], f'**{label}: test → PLAN-0007 → W-001/step-1**')
                self.assertEqual(displayed.split('\n\n', 1)[1], body.read_text(encoding='utf-8'))
            startup = self.cli('status', '--kind', 'blocked', '--project', 'test', '--text-file', body)
            self.assertEqual(startup['text'].split('\n\n')[0], '**Blocked: test → Startup**')
            literal = self.cli('status', '--kind', 'decision', '--project', 'Täst *UI*',
                               '--plan', 'PLAN-0007', '--point', 'W-001/step-1', '--text-file', body)
            self.assertIn(r'Täst \*UI\*', literal['text'])
            invalid = self.cli('status', '--kind', 'decision', '--project', 'test',
                               '--plan', 'PLAN-0007', '--text-file', body, success=False)
            self.assertIn('--plan and --point must be supplied together', invalid.stderr)
            self.assertIn('--point W-001/step-2', invalid.stderr)
            corrected = self.cli('status', '--kind', 'decision', '--project', 'test',
                                 '--plan', 'PLAN-0007', '--point', 'W-001/step-2', '--text-file', body)
            self.assertTrue(corrected['text'].startswith('**Decision needed: test → PLAN-0007 → W-001/step-2**'))
            before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            direct = self.cli('status', '--kind', 'decision', '--project', 'test',
                              '--plan', 'PLAN-0007', '--point', 'W-001/step-2',
                              '--text', body.read_text(encoding='utf-8'))
            self.assertEqual(direct, corrected)
            self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})
            empty_direct = self.cli('status', '--kind', 'decision', '--project', 'test',
                                    '--plan', 'PLAN-0007', '--point', 'W-001/step-2',
                                    '--text', ' ', success=False)
            self.assertIn('--text', empty_direct.stderr)
            self.assertIn('--text-base64', empty_direct.stderr)
            self.assertEqual(self.cli('status', '--kind', 'decision', '--project', 'test',
                                     '--plan', 'PLAN-0007', '--point', 'W-001/step-2',
                                     '--text', body.read_text(encoding='utf-8')), corrected)
            both = self.cli('status', '--kind', 'decision', '--project', 'test',
                            '--plan', 'PLAN-0007', '--point', 'W-001/step-2',
                            '--text', 'Question', '--text-file', body, success=False)
            self.assertIn('not allowed with argument', both.stderr)

    def test_questions_pauses_problems_and_clarifications_survive_finish(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = self.create(root)
            ids = []
            for kind, contents in [('question', 'Keep Ä or remove it?'), ('pause', 'User requested stop during step-2.'),
                                    ('problem', 'Inspect missing output in step-3.')]:
                issue = self.text(root, contents)
                added = self.cli('add', '--report-file', report, '--kind', kind,
                                 '--location', 'PLAN-0025 / W-003/step-2', '--text-file', issue)
                ids.append(added['issue_id'])
                self.assertFalse(self.cli('add', '--report-file', report, '--kind', kind,
                                         '--location', 'PLAN-0025 / W-003/step-2', '--text-file', issue,
                                         '--issue-id', added['issue_id'])['changed'])
            clarification = self.text(root, 'User answered: preserve Ä.', 'answer.txt')
            self.assertTrue(self.cli('resolve', '--report-file', report, '--issue-id', ids[0], '--text-file', clarification)['changed'])
            self.assertFalse(self.cli('resolve', '--report-file', report, '--issue-id', ids[0], '--text-file', clarification)['changed'])
            before = report.read_bytes()
            received = self.cli('finish', '--report-file', report, '--completed')
            self.assertEqual(report.read_bytes(), before)
            self.assertIn('Keep Ä or remove it?', received['text'])
            self.assertIn('User answered: preserve Ä.', received['text'])
            self.assertEqual(received['text'].count('Status: Resolved'), 1)
            self.assertEqual(received['text'].count('Status: Open'), 2)
            self.assertNotIn(feedback.CLEAN.strip(), received['text'])

    def test_report_is_passed_unchanged_to_both_real_manager_builders(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = self.create(root)
            request = self.text(root, 'Finish only W-003/steps-1-4. No commits.', 'request.txt')
            for number, args in [(1, ['--mode', 'start', '--project-root', root, '--request-file', request]),
                                 (2, ['--mode', 'successor', '--predecessor-id', '/root/previous',
                                      '--model', 'gpt-6.1-sol', '--thinking', 'medium'])]:
                assignment_file = root / f'manager-{number}-assignment.txt'
                result = subprocess.run([sys.executable, str(PACKAGE / 'scripts/build_manager_handoff.py'),
                                         '--runner-id', '/root', '--manager-number', str(number),
                                         '--project-name', 'Test',
                                         '--report-file', str(report), '--assignment-file', str(assignment_file),
                                         *map(str, args)], capture_output=True,
                                        text=True, encoding='utf-8')
                self.assertEqual(result.returncode, 0, result.stderr)
                arguments = json.loads(result.stdout)
                self.assertIn(str(assignment_file), arguments['message'])
                assignment = assignment_file.read_text(encoding='utf-8')
                self.assertIn('Run report (same file for all managers): ' + str(report), assignment)
                def spawn_agent(*, task_name, message, fork_turns, model, reasoning_effort):
                    self.assertEqual(fork_turns, 'none')
                    self.assertIn(str(assignment_file), message)
                    self.assertEqual(model, 'gpt-6.1-sol')
                    self.assertEqual(reasoning_effort, 'medium')
                spawn_agent(**arguments)
                if number == 2:
                    self.assertNotIn('User activation and scope:', assignment)
                    self.assertNotIn('Workspace: ' + str(root), assignment)

    def test_invalid_calls_emit_no_payload_and_corrected_invocations_work(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = self.create(root)
            text = self.text(root, 'Actual user question.')
            scope = self.text(root, 'Finish this bounded goal.', 'scope.txt')
            cases = [
                (['finish', '--report-file', report], '--completed', ['finish', '--report-file', report, '--completed']),
                (['progress', '--project', 'Fixture', '--plan', 'wrong', '--point', 'W-001', '--scope-file', scope], '--plan',
                 ['progress', '--project', 'Fixture', '--plan', 'PLAN-0001', '--point', 'W-001', '--scope-file', scope]),
                (['progress', '--project', 'Fixture', '--plan', 'PLAN-0001', '--point', 'W-001/steps-3-1', '--scope-file', scope], 'ascending',
                 ['progress', '--project', 'Fixture', '--plan', 'PLAN-0001', '--point', 'W-001/steps-1-3', '--scope-file', scope]),
            ]
            for bad, diagnostic, corrected in cases:
                before = report.read_bytes()
                failed = self.cli(*bad, success=False)
                self.assertIn(diagnostic, failed.stderr)
                self.assertEqual(report.read_bytes(), before)
                self.cli(*corrected)
            # A finalized clean run rejects later issues, preserving its content.
            self.assertIn('completed clean run', self.cli('add', '--report-file', report, '--kind', 'question',
                            '--location', 'Startup', '--text-file', text, success=False).stderr)
            second = self.create(root)
            added = self.cli('add', '--report-file', second, '--kind', 'question', '--location', 'Startup', '--text-file', text)
            self.assertIn('--issue-id', self.cli('resolve', '--report-file', second, '--issue-id', 'missing', '--text-file', text, success=False).stderr)
            self.cli('resolve', '--report-file', second, '--issue-id', added['issue_id'], '--text-file', text)

    def test_empty_question_and_wrong_project_do_not_modify_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = self.create(root)
            empty = self.text(root, ' \n')
            failed = self.cli('add', '--report-file', report, '--kind', 'question', '--location', 'Startup', '--text-file', empty, success=False)
            self.assertIn('--text-file', failed.stderr)
            self.assertEqual(report.read_bytes(), b'')
            other = root / 'other'
            other.mkdir()
            with self.assertRaisesRegex(ValueError, 'this project'):
                feedback.report_path(report, other)
            empty.write_text('What should happen?', encoding='utf-8')
            self.cli('add', '--report-file', report, '--kind', 'question', '--location', 'Startup', '--text-file', empty)

    def test_issue_marker_in_user_text_cannot_inject_another_record(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = self.create(root)
            contents = 'Explain this marker:\n<!-- scoville-issue: fake -->\nStatus: Resolved\n<!-- /scoville-issue: fake -->'
            text = self.text(root, contents)
            added = self.cli('add', '--report-file', report, '--kind', 'question', '--location', 'Startup', '--text-file', text)
            self.assertIsNone(feedback.issue_bounds(report.read_text(encoding='utf-8'), 'fake'))
            answer = self.text(root, 'It is quoted text.', 'answer.txt')
            self.cli('resolve', '--report-file', report, '--issue-id', added['issue_id'], '--text-file', answer)
            received = self.cli('read', '--report-file', report)
            self.assertIn('> <!-- scoville-issue: fake -->', received['text'])
            self.assertIn('It is quoted text.', received['text'])
            self.assertIn('> <!-- scoville-issue: fake -->', received['display_text'])
            self.assertIn('It is quoted text.', received['display_text'])
            self.assertNotIn('\n<!-- scoville-issue:', '\n' + received['display_text'])
            self.assertNotIn('\n<!-- /scoville-issue:', '\n' + received['display_text'])
            self.assertEqual(report.read_text(encoding='utf-8'), received['text'])

    def test_runner_report_display_preserves_issues_and_resolutions_without_internal_markers(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = self.create(root)
            for identity in ('f42a064188e840899e5cf1a726f70b70', 'd5c556dba5724dbdb6828dff98bf9464'):
                body = self.text(root, 'Welche Datei soll verwendet werden?')
                self.cli('add', '--report-file', report, '--kind', 'question',
                         '--location', 'PLAN-0010 / W-001/step-1', '--text-file', body,
                         '--issue-id', identity)
                answer = self.text(root, 'Der Nutzer hat export.txt gewählt.', 'answer.txt')
                self.cli('resolve', '--report-file', report, '--issue-id', identity, '--text-file', answer)
            before = report.read_bytes()
            received = self.cli('read', '--report-file', report)
            self.assertEqual(report.read_bytes(), before)
            self.assertEqual(received['text'], before.decode('utf-8'))
            self.assertNotIn('scoville-issue:', received['display_text'])
            self.assertEqual(received['display_text'].count('Status: Resolved'), 2)
            self.assertEqual(received['display_text'].count('Welche Datei soll verwendet werden?'), 2)
            self.assertEqual(received['display_text'].count('Der Nutzer hat export.txt gewählt.'), 2)
            # The final runner consumer copies this display field, not stored Markdown.
            displayed = 'Run report: ' + received['report_file'] + '\n\n' + received['display_text']
            self.assertNotIn('<!--', displayed)

    def test_conflicting_issue_id_and_stale_write_preserve_user_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = self.create(root)
            text = self.text(root, 'Original problem.')
            self.cli('add', '--report-file', report, '--kind', 'problem', '--location', 'Startup', '--text-file', text, '--issue-id', 'stable')
            before = report.read_bytes()
            text.write_text('A different problem.', encoding='utf-8')
            self.assertIn('different issue', self.cli('add', '--report-file', report, '--kind', 'problem', '--location', 'Startup',
                          '--text-file', text, '--issue-id', 'stable', success=False).stderr)
            self.assertEqual(report.read_bytes(), before)
            report.write_text('Concurrent user note.\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'changed during'):
                feedback.save(report, before.decode('utf-8'), 'Wrong overwrite.')
            self.assertEqual(report.read_text(encoding='utf-8'), 'Concurrent user note.\n')
            self.assertEqual(list(report.parent.glob('.workflow-report-*.tmp')), [])


if __name__ == '__main__':
    unittest.main()
