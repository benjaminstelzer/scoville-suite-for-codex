"""Real packaged builders consumed as native creation arguments."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_contract import PACKAGE, SUITE_ROOT, _builder, _config

ID = '01a0e778-0c80-7660-b8b9-c8ce59a9fed4'


class NativeCreationTests(unittest.TestCase):
    def run_builder(self, script, *arguments):
        return subprocess.run([sys.executable, str(PACKAGE / 'scripts' / script), *map(str, arguments)],
                              env={**os.environ, 'CODEX_THREAD_ID': ID}, capture_output=True,
                              text=True, encoding='utf-8')

    def consume(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        # Bind the generated payload unchanged to the exposed native schema.
        # Live host dispatch is a separate integration check.
        def spawn_agent(*, task_name, message, fork_turns, model, reasoning_effort):
            self.assertRegex(task_name, r'^scoville_(executor|reviewer)_[0-9]+(?:_[0-9a-f]+)?$')
            self.assertEqual(fork_turns, 'none')
            self.assertEqual(model, 'gpt-6-sol')
            self.assertEqual(reasoning_effort, 'high')
            self.assertIn('manager_agent_id=/root/manager', message)
            self.assertNotIn('send_message_to_thread', message)
            self.assertNotIn('set_thread_archived', message)
        spawn_agent(**data)
        return data

    def test_dispatch_titles_cover_full_units_review_and_correction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            evidence = root / 'result.txt'
            evidence.write_text('completed: checked change; remaining work unchanged', encoding='utf-8')
            common = ['--project-root', root, '--format', 'create', '--manager-agent-id', '/root/manager',
                      '--project-name', 'Änderung 中文', '--worker-number', '7', '--model', 'gpt-6-sol', '--thinking', 'high']
            whole = self.consume(self.run_builder('build_dispatch_prompt.py', *common, '--unit', 'W-001', '--role', 'executor'))
            self.assertIn('Assignment: SC-WRK-7: Änderung 中文 · PLAN-0001/W-001/steps-1-2', whole['message'])
            for role, extra, label in [('executor', [], 'SC-WRK'), ('reviewer', ['--executor-result', evidence], 'SC-REV'),
                                       ('executor', ['--reviewer-result', evidence], 'SC-WRK')]:
                result = self.consume(self.run_builder('build_dispatch_prompt.py', *common, '--unit', 'W-001/step-1', '--role', role, *extra))
                self.assertIn(f'Assignment: {label}-7: Änderung 中文 · PLAN-0001/W-001/step-1', result['message'])
                self.assertEqual(result['task_name'], f'scoville_{role}_7')
                # These are generated instruction-contract checks, not proof
                # that a live agent completes its assignment after crossing.
                for rule in (
                    'rollover_pending does not stop or shorten your assignment',
                    'finish the complete assigned Step or Step group, review or repair, including required corrections and checks',
                    'Do not return context_handoff with unfinished assigned work merely because a threshold was crossed',
                ):
                    self.assertIn(rule, result['message'])
                if role == 'executor':
                    self.assertIn('Use completed when your assigned implementation and checks are finished', result['message'])
                    self.assertIn('even if manager review or Plan closure remains', result['message'])
                    self.assertIn('specific work still assigned to you after review', result['message'])
                self.assertIn(str(PACKAGE.parent / 'scoville-code' / 'SKILL.md'), result['message'])
                self.assertTrue((PACKAGE.parent / 'scoville-code' / 'SKILL.md').is_file())
                self.assertIn('Treat a user stop as immediate', result['message'])
                self.assertNotIn('On context_handoff, state finished Steps', result['message'])
            invalid = self.run_builder('build_dispatch_prompt.py', *common, '--unit', 'W-001/step-1', '--role', 'reviewer')
            self.assertNotEqual(invalid.returncode, 0)
            self.assertEqual(invalid.stdout, '')
            self.assertIn('usage:', invalid.stderr)
            self.assertIn('--executor-result', invalid.stderr)

    def test_wrapped_release_assignment_loads_the_real_sibling_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            project = base / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', project)
            for name in ('scoville-code', 'scoville-workflow-for-codex'):
                member = next(m for m in _config['members'] if m['name'] == name)
                for relative, content in _builder.payload(SUITE_ROOT, member, _config).items():
                    target = base / 'packages' / name / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(content)
            script = base / 'packages/scoville-workflow-for-codex/scoville-workflow-for-codex/scripts/build_dispatch_prompt.py'
            code = base / 'packages/scoville-code/scoville-code/SKILL.md'
            assignment = project / 'assignment.txt'
            command = [sys.executable, '-B', str(script), '--project-root', str(project), '--unit', 'W-001',
                       '--role', 'executor', '--format', 'create', '--manager-agent-id', '/root/manager',
                       '--project-name', 'fixture', '--worker-number', '7', '--model', 'gpt-6-sol', '--thinking', 'high',
                       '--assignment-file', str(assignment)]
            content = code.read_bytes()
            code.unlink()
            failed = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(failed.stdout, '')
            self.assertIn('complete matching suite package layout', failed.stderr)
            self.assertFalse(assignment.exists())
            code.write_bytes(content)
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            self.consume(result)
            self.assertIn(str(code), assignment.read_text(encoding='utf-8'))
            self.assertEqual(code.read_bytes(), content)

    def test_prior_code_fix_pauses_and_resumes_the_full_group_after_review(self):
        # Contract coverage through the packaged CLI and native argument consumer;
        # actual agent pause/resume and measured rollover remain live acceptance.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            facts, result = root / 'facts.txt', root / 'result.txt'
            facts.write_text('Assigned group: fix previously checked product code if needed, then finish dependent tests. '
                             'rollover_pending was measured before the fix; keep the full assigned group.', encoding='utf-8')
            common = ['--project-root', root, '--format', 'create', '--manager-agent-id', '/root/manager',
                      '--project-name', 'Fixture', '--model', 'gpt-6-sol', '--thinking', 'high',
                      '--unit', 'W-001/steps-1-2', '--supplemental-context', facts]
            worker = self.consume(self.run_builder('build_dispatch_prompt.py', *common,
                                  '--role', 'executor', '--worker-number', '7'))
            for rule in ('return review_pending', 'including after rollover_pending',
                         'This pauses the same assignment', 'only after the manager confirms review acceptance',
                         'or review acceptance', 'completed, review_pending, blocked'):
                self.assertIn(rule, worker['message'])
            self.assertNotIn('completes your assignment after focused checks', worker['message'])
            self.assertIn('W-001/steps-1-2', worker['message'])
            paused = 'review_pending: prior-code fix checked; dependent tests remain. Retained rollover_pending: 61/100 percent.'
            result.write_text(paused, encoding='utf-8')
            review = self.consume(self.run_builder('build_dispatch_prompt.py', *common,
                                  '--role', 'reviewer', '--worker-number', '7', '--executor-result', result))
            self.assertIn(paused, review['message'])
            self.assertIn('Stay read-only.', review['message'])
            self.assertNotIn('completed, review_pending, blocked', review['message'])
            finding = 'changes_requested: the checked fix misses rollback; correct rollback before dependent tests resume.'
            result.write_text(finding, encoding='utf-8')
            repair = self.consume(self.run_builder('build_dispatch_prompt.py', *common,
                                  '--role', 'executor', '--worker-number', '8', '--reviewer-result', result))
            self.assertIn(finding, repair['message'])
            self.assertNotEqual(worker['task_name'], repair['task_name'])
            operations = (PACKAGE / 'references/operations.md').read_text(encoding='utf-8')
            for rule in ('review_pending is a pause, not assignment completion',
                         'Do not mark the unit complete or roll over the manager at this pause',
                         'keep the original worker write-inactive', 'resume that exact worker with `followup_task`',
                         'Retain any measured rollover_pending', 'before dependent tests or work continue'):
                self.assertIn(rule, operations)
            self.assertNotIn('even inside a larger test Step', operations)

    def test_file_assignment_preserves_full_text_and_native_parameters(self):
        # The actual file reader consumes the packaged helper output. Native
        # agent interpretation is separate live evidence.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            facts = root / 'facts.txt'
            body = 'Keep no third-party dependencies. Quotes: "A" and \'B\'.\nScope: Änderung 中文 → exact\\path.\n'
            facts.write_text(body, encoding='utf-8')
            result = root / 'result.txt'
            result.write_text('completed: checked result, unchanged scope.', encoding='utf-8')
            common = ['--project-root', root, '--format', 'create', '--manager-agent-id', '/root/manager',
                      '--project-name', 'Änderung 中文', '--worker-number', '9', '--model', 'gpt-6-sol',
                      '--thinking', 'high', '--unit', 'W-001/steps-1-2', '--supplemental-context', facts]
            for role, extra in [('executor', []), ('reviewer', ['--executor-result', result])]:
                with self.subTest(role=role):
                    full = self.consume(self.run_builder('build_dispatch_prompt.py', *common, '--role', role, *extra))
                    assignment = root / f'{role}-assignment.txt'
                    short = self.consume(self.run_builder('build_dispatch_prompt.py', *common, '--role', role,
                                         *extra, '--assignment-file', assignment))
                    self.assertEqual(assignment.read_bytes(), full['message'].encode('utf-8'))
                    self.assertIn(body, assignment.read_text(encoding='utf-8'))
                    self.assertIn(str(assignment), short['message'])
                    self.assertNotIn(body, short['message'])
                    self.assertEqual({k: v for k, v in full.items() if k != 'message'},
                                     {k: v for k, v in short.items() if k != 'message'})
                    if role == 'reviewer': self.assertIn('Stay read-only.', short['message'])

    def test_file_assignment_rejects_overwrite_and_invalid_mode_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            common = ['--project-root', root, '--format', 'create', '--manager-agent-id', '/root/manager',
                      '--project-name', 'Fixture', '--worker-number', '9', '--model', 'gpt-6-sol',
                      '--thinking', 'high', '--unit', 'W-001/step-1', '--role', 'executor']
            existing = root / 'existing.txt'
            existing.write_bytes(b'Preserve prior assignment.\r\n')
            cases = [(['--assignment-file', existing], 'already exists'),
                     (['--assignment-file', root / 'missing' / 'new.txt'], 'existing absolute directory'),
                     (['--assignment-file', 'relative.txt'], 'existing absolute directory'),
                     (['--format', 'prompt', '--assignment-file', root / 'text.txt'], '--format create'),
                     (['--predecessor-agent-id', '/root/old', '--assignment-file', root / 'recovery.txt'], 'fresh child')]
            before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            for extra, diagnostic in cases:
                with self.subTest(extra=extra):
                    failed = self.run_builder('build_dispatch_prompt.py', *common, *extra)
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertEqual(failed.stdout, '')
                    self.assertIn(diagnostic, failed.stderr)
                    self.assertIn('usage:', failed.stderr)
                    self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})
            self.consume(self.run_builder('build_dispatch_prompt.py', *common,
                         '--assignment-file', root / 'corrected.txt'))

    def test_invalid_model_leaves_no_assignment_and_same_path_can_be_retried(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            common = ['--project-root', root, '--format', 'create', '--manager-agent-id', '/root/manager',
                      '--project-name', 'Fixture', '--worker-number', '9', '--thinking', 'high',
                      '--unit', 'W-001/step-1', '--role', 'executor']
            for number, model in enumerate(('', ' ', 'gpt-6-sol\nother', 'gpt-6-sol\rother')):
                with self.subTest(model=model):
                    assignment = root / f'assignment-{number}.txt'
                    before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
                    failed = self.run_builder('build_dispatch_prompt.py', *common,
                                              '--model', model, '--assignment-file', assignment)
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertEqual(failed.stdout, '')
                    self.assertIn('--model must be nonempty single-line text', failed.stderr)
                    self.assertIn('usage:', failed.stderr)
                    self.assertFalse(assignment.exists())
                    self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})
                    corrected = self.consume(self.run_builder('build_dispatch_prompt.py', *common,
                                             '--model', 'gpt-6-sol', '--assignment-file', assignment))
                    self.assertIn(str(assignment), corrected['message'])
                    self.assertIn('## Assigned unit', assignment.read_text(encoding='utf-8'))

    def test_missing_create_arguments_have_actionable_diagnostics(self):
        result = self.run_builder('build_dispatch_prompt.py', '--project-root', PACKAGE,
                                  '--role', 'executor', '--unit', 'W-001', '--format', 'create', '--manager-agent-id', '/root/manager')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        for parameter in ('--worker-number', '--project-name', '--model', '--thinking'):
            self.assertIn(parameter, result.stderr)
        self.assertIn('usage:', result.stderr)

    def test_child_continuations_and_invalid_identity_then_correction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            handoff, facts = root / 'handoff.txt', root / 'facts.txt'
            handoff.write_text('Checks A passed; only B remains.', encoding='utf-8')
            facts.write_text('B must pass. No publication. The user authorized this recovery transfer and internal coordination.', encoding='utf-8')
            common = ['--project-root', root, '--format', 'create', '--project-name', 'Fixture',
                      '--worker-number', '8', '--model', 'gpt-6-sol', '--thinking', 'high',
                      '--unit', 'W-001/step-1']
            for role in ('executor', 'reviewer'):
                continuation = ['--role', role, '--context-handoff', handoff, '--supplemental-context', facts]
                cases = [
                    ([], '--manager-agent-id'),
                    (['--manager-agent-id', 'bad\nID'], '--manager-agent-id'),
                    (['--manager-agent-id', '/root/manager'], '--predecessor-agent-id'),
                    (['--manager-agent-id', '/root/manager', '--predecessor-agent-id', '/root/manager'], '--predecessor-agent-id'),
                    (['--manager-agent-id', '/root/manager', '--predecessor-agent-id', 'bad\nID'], '--predecessor-agent-id'),
                ]
                for bad, diagnostic in cases:
                    failed = self.run_builder('build_dispatch_prompt.py', *common, *continuation, *bad)
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertEqual(failed.stdout, '')
                    self.assertIn(diagnostic, failed.stderr)
                names = []
                for predecessor in ('/root/old/worker', '/root/new/worker'):
                    result = self.consume(self.run_builder('build_dispatch_prompt.py', *common, *continuation,
                        '--manager-agent-id', '/root/manager', '--predecessor-agent-id', predecessor))
                    self.assertTrue(result['message'].startswith('FIRST ACTION'))
                    self.assertIn('target=/root/manager and message=HANDOFF_ACCEPTED ' + predecessor, result['message'])
                    self.assertNotIn('target=' + predecessor, result['message'])
                    self.assertNotIn('## Work Item context', result['message'])
                    names.append(result['task_name'])
                self.assertNotEqual(*names)

    def create_report(self, root):
        result = self.run_builder('run_feedback.py', 'create', '--project-root', root)
        self.assertEqual(result.returncode, 0, result.stderr)
        return Path(json.loads(result.stdout)['report_file'])

    def consume_manager(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        # Bind to the exposed collaboration schema. Live agent acceptance is a
        # separate host check; this does not simulate READY or START delivery.
        def spawn_agent(*, task_name, message, fork_turns, model=None, reasoning_effort=None):
            self.assertEqual(fork_turns, 'none')
            self.assertTrue(task_name)
            self.assertTrue(message)
            self.assertEqual(model is None, reasoning_effort is None)
        spawn_agent(**data)
        return data

    def test_manager_start_and_successor_have_separate_context(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = root / 'request.txt'
            body = 'Start Scoville Workflow for the active Plan. Internal coordination authorized.'
            request.write_text(body, encoding='utf-8')
            report = self.create_report(root)
            common = ['--runner-id', '/root', '--manager-number', '1', '--report-file', report]
            start = self.consume_manager(self.run_builder('build_manager_handoff.py', *common,
                '--mode', 'start', '--project-root', root, '--request-file', request))
            self.assertEqual(start['task_name'], 'scoville_manager_1')
            self.assertIn(body, start['message'])
            self.assertIn(str(root), start['message'])
            self.assertNotIn('model', start)
            successor = self.consume_manager(self.run_builder('build_manager_handoff.py', *common,
                '--mode', 'successor', '--predecessor-id', 'manager-exact-id',
                '--model', 'gpt-6-astra', '--thinking', 'high'))
            self.assertEqual(successor['model'], 'gpt-6-astra')
            self.assertEqual(successor['reasoning_effort'], 'high')
            self.assertIn('Predecessor: manager-exact-id', successor['message'])
            self.assertNotIn(body, successor['message'])
            self.assertNotIn('Workspace: ' + str(root), successor['message'])
            self.assertIn('Run report (same file for all managers): ' + str(report), successor['message'])
            self.assertNotIn('User activation and scope:', successor['message'])
            self.assertNotIn('create_thread', successor['message'])
            for data in (start, successor):
                self.assertIn('send READY', data['message'])
                self.assertIn('Wait for START from that exact runner', data['message'])
                self.assertIn('including in your final answer', data['message'])
                self.assertIn('Context thresholds only schedule rollover', data['message'])
                self.assertIn('including required checks, due review, repairs, Plan updates and authorized commits', data['message'])
                self.assertIn('confirm all children and writes are quiescent before requesting a successor', data['message'])
                self.assertIn('A user stop remains immediate', data['message'])
                self.assertIn('Report rejected or pending takeover as BLOCKED', data['message'])
                self.assertIn('never use RUNNING CONTROL', data['message'])

    def test_manager_invalid_calls_then_corrected_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = root / 'request.txt'
            request.write_text('Start Scoville Workflow.', encoding='utf-8')
            report = self.create_report(root)
            common = ['--runner-id', '/root', '--manager-number', '2', '--report-file', report]
            successor = ['--mode', 'successor', '--predecessor-id', 'old-manager']
            cases = [
                (['--mode', 'successor'], '--predecessor-id', successor),
                (successor + ['--request-file', request], 'omit --request-file', successor),
                (successor + ['--project-root', root], 'omit --request-file', successor),
                (successor + ['--model', 'gpt-6-astra'], 'both --model and --thinking',
                 successor + ['--model', 'gpt-6-astra', '--thinking', 'high']),
                (['--mode', 'successor', '--predecessor-id', '/root'], 'not --runner-id', successor),
                (['--mode', 'start'], '--project-root',
                 ['--mode', 'start', '--project-root', root, '--request-file', request]),
                (['--mode', 'start', '--project-root', root], '--request-file',
                 ['--mode', 'start', '--project-root', root, '--request-file', request]),
                (successor + ['--manager-number', '0'], 'positive integer', successor),
                (successor + ['--runner-id', 'bad\nID'], '--runner-id', successor),
            ]
            for bad, diagnostic, corrected in cases:
                with self.subTest(arguments=bad):
                    failed = self.run_builder('build_manager_handoff.py', *common, *bad)
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertEqual(failed.stdout, '')
                    self.assertIn(diagnostic, failed.stderr)
                    self.assertIn('usage:', failed.stderr)
                    self.consume_manager(self.run_builder('build_manager_handoff.py', *common, *corrected))

    def test_start_request_failures_emit_no_spawn_payload(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = root / 'activation.txt'
            report = self.create_report(root)
            common = ['--runner-id', '/root', '--manager-number', '1', '--report-file', report, '--mode', 'start',
                      '--project-root', root, '--request-file', request]
            for contents, diagnostic in ((None, 'activation.txt'), (b' \r\n', 'empty'),
                                         (b'\xff', 'utf-8')):
                with self.subTest(contents=contents):
                    if contents is not None:
                        request.write_bytes(contents)
                    failed = self.run_builder('build_manager_handoff.py', *common)
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertEqual(failed.stdout, '')
                    self.assertIn(diagnostic, failed.stderr)
                    self.assertIn('usage:', failed.stderr)
            request.write_text('Start Workflow only for W-001. No commits.', encoding='utf-8')
            result = self.consume_manager(self.run_builder('build_manager_handoff.py', *common))
            self.assertIn('Start Workflow only for W-001. No commits.', result['message'])

    def test_successor_rejects_empty_or_multiline_predecessor(self):
        with tempfile.TemporaryDirectory() as directory:
            report = self.create_report(Path(directory))
            common = ['--runner-id', '/root', '--manager-number', '2', '--mode', 'successor', '--report-file', report]
            for identity in ('', '  ', 'old\nother', 'old\rother'):
                with self.subTest(identity=identity):
                    failed = self.run_builder('build_manager_handoff.py', *common,
                                              '--predecessor-id', identity)
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertEqual(failed.stdout, '')
                    self.assertIn('--predecessor-id', failed.stderr)
                    self.assertIn('usage:', failed.stderr)
            self.consume_manager(self.run_builder('build_manager_handoff.py', *common,
                                 '--predecessor-id', '/root/old_manager'))

    def test_child_rejects_missing_handoff_and_empty_constraints(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            handoff, facts = root / 'handoff.txt', root / 'facts.txt'
            facts.write_text('No commits. Check B only.', encoding='utf-8')
            common = ['--project-root', root, '--format', 'create', '--project-name', 'Fixture',
                      '--worker-number', '8', '--model', 'gpt-6-sol', '--thinking', 'high',
                      '--unit', 'W-001/step-1', '--role', 'executor',
                      '--manager-agent-id', '/root/manager', '--predecessor-agent-id', '/root/old',
                      '--context-handoff', handoff, '--supplemental-context', facts]
            failed = self.run_builder('build_dispatch_prompt.py', *common)
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(failed.stdout, '')
            self.assertIn('handoff.txt', failed.stderr)
            self.assertIn('usage:', failed.stderr)
            handoff.write_text('A passed. Only B remains.', encoding='utf-8')
            facts.write_text(' \n', encoding='utf-8')
            failed = self.run_builder('build_dispatch_prompt.py', *common)
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(failed.stdout, '')
            self.assertIn('--supplemental-context', failed.stderr)
            facts.write_text('No commits. Check B only.', encoding='utf-8')
            result = self.consume(self.run_builder('build_dispatch_prompt.py', *common))
            self.assertIn('A passed. Only B remains.', result['message'])
            self.assertIn('No commits. Check B only.', result['message'])


if __name__ == '__main__':
    unittest.main()
