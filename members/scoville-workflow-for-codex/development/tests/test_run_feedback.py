"""Consume the packaged CLI in manager startup, issue recovery and final display."""
import importlib.util
import json
from pathlib import Path
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
            self.assertEqual(first.parent, root / '.scoville')
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
            self.assertIn('--text or --text-file must supply', empty_direct.stderr)
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
                result = subprocess.run([sys.executable, str(PACKAGE / 'scripts/build_manager_handoff.py'),
                                         '--runner-id', '/root', '--manager-number', str(number),
                                         '--project-name', 'Test',
                                         '--report-file', str(report), *map(str, args)], capture_output=True,
                                        text=True, encoding='utf-8')
                self.assertEqual(result.returncode, 0, result.stderr)
                arguments = json.loads(result.stdout)
                self.assertIn('Run report (same file for all managers): ' + str(report), arguments['message'])
                def spawn_agent(*, task_name, message, fork_turns, model, reasoning_effort):
                    self.assertEqual(fork_turns, 'none')
                    self.assertIn('WORKING_ON', message)
                    self.assertEqual(model, 'gpt-6.1-sol')
                    self.assertEqual(reasoning_effort, 'medium')
                spawn_agent(**arguments)
                if number == 2:
                    self.assertNotIn('User activation and scope:', arguments['message'])
                    self.assertNotIn('Workspace: ' + str(root), arguments['message'])

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
