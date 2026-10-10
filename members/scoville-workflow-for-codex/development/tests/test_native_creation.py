"""Real packaged builders consumed as native creation arguments."""
import json
import os
import re
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid

from test_contract import PACKAGE, SUITE_ROOT, _builder, _config

ID = '01a0e778-0c80-7660-b8b9-c8ce59a9fed4'


class NativeCreationTests(unittest.TestCase):
    def test_start_request_failure_then_complete_manager_consumer(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project Ä 中文'
            root.mkdir()
            request = root / 'request Ä 中文.txt'
            assignment = root / 'manager-assignment.txt'
            report = self.create_report(root)
            arguments = ['--mode', 'start', '--runner-id', '/root', '--project-name', 'Fixture',
                '--manager-number', '1', '--project-root', root, '--request-file', request,
                '--report-file', report, '--assignment-file', assignment]
            for invalid in (None, b'\xff'):
                if invalid is not None:
                    request.write_bytes(invalid)
                failed = self.run_builder('build_manager_handoff.py', *arguments)
                self.assertNotEqual(failed.returncode, 0)
                self.assertEqual(failed.stdout, '')
                self.assertIn('Invalid argument --request-file', failed.stderr)
                self.assertIn(str(request), failed.stderr)
                self.assertIn('existing readable UTF-8 file', failed.stderr)
                self.assertIn('usage:', failed.stderr)
                self.assertFalse(assignment.exists())
                self.assertEqual(report.read_bytes(), b'')
            body = 'Start complete authorized scope Ä 中文: `literal`, $(not-a-command), "quotes", apostrophe\'s and exact\\path.'
            request.write_text(body, encoding='utf-8', newline='\n')
            self.assertEqual(request.read_bytes(), body.encode('utf-8'))
            payload = self.consume_manager(self.run_builder('build_manager_handoff.py', *arguments))
            self.assertIn(str(assignment), payload['message'])
            delivered = assignment.read_text(encoding='utf-8')
            self.assertIn('User activation and scope:\n' + body + '\n', delivered)
            self.assertEqual(assignment.read_bytes(), delivered.encode('utf-8'))
            self.assertEqual(report.read_bytes(), b'')

    def test_role_input_failures_then_literal_safe_complete_consumer(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'project Ä 中文'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            facts = base / 'facts.txt'
            facts.write_text('Review only this assigned unit. No commits.', encoding='utf-8')
            for flag, role in [('--executor-result', 'reviewer'), ('--reviewer-result', 'executor'),
                               ('--context-handoff', 'executor'), ('--supplemental-context', 'executor')]:
                with self.subTest(flag=flag):
                    source = base / (flag[2:] + ' Ä 中文.txt')
                    assignment = base / (flag[2:] + '-assignment.txt')
                    arguments = ['--project-root', root, '--format', 'create', '--project-name', 'Fixture',
                        '--worker-number', '1', '--model', 'gpt-6-sol', '--thinking', 'high',
                        '--unit', 'W-001/step-1', '--role', role, '--manager-agent-id', '/root/manager',
                        '--assignment-file', assignment, flag, source]
                    if flag != '--supplemental-context':
                        arguments.extend(['--supplemental-context', facts])
                    if flag == '--context-handoff':
                        arguments.extend(['--predecessor-agent-id', '/root/previous'])
                    for invalid in (None, b'\xff'):
                        if invalid is not None:
                            source.write_bytes(invalid)
                        failed = self.run_builder('build_dispatch_prompt.py', *arguments, auto_file=False)
                        self.assertNotEqual(failed.returncode, 0)
                        self.assertEqual(failed.stdout, '')
                        self.assertIn('Invalid argument ' + flag, failed.stderr)
                        self.assertIn(str(source), failed.stderr)
                        self.assertIn('UTF-8', failed.stderr)
                        self.assertIn('usage:', failed.stderr)
                        self.assertFalse(assignment.exists())
                    literal = 'Retained complete result Ä 中文: `node -e "process.exit(17)"`, $(not-a-command), exact\\path.\n'
                    source.write_text(literal, encoding='utf-8', newline='\n')
                    self.assertEqual(source.read_bytes(), literal.encode('utf-8'))
                    corrected = self.run_builder('build_dispatch_prompt.py', *arguments, auto_file=False)
                    payload = self.consume(corrected)
                    received = self.prompt(payload)
                    self.assertIn('## ' + flag[2:].replace('-', '_') + '\n' + literal, received)
                    self.assertEqual(assignment.read_bytes(), received.encode('utf-8'))

    def test_documented_fresh_commands_deliver_complete_file_assignments(self):
        instructions = (PACKAGE / 'references/operations-dispatch.md').read_text(encoding='utf-8')
        examples = [block.strip() for block in re.findall(r'```text\n(.*?)\n```', instructions, re.S)
                    if 'build_dispatch_prompt.py' in block and '--format create' in block]
        self.assertEqual(len(examples), 2)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project with spaces'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            config = root / '.scoville/config.json'
            config.parent.mkdir(exist_ok=True)
            pair = {'low': {'model': 'gpt-6-sol', 'reasoning': 'high'}}
            config.write_text(json.dumps({'workflow': {'execute': pair, 'review': pair}}), encoding='utf-8')
            facts = root / 'facts.txt'
            body = 'Preserve this full assignment fact: Änderung 中文, `literal` and exact\\path.\n' * 200
            facts.write_text(body, encoding='utf-8')
            result = root / 'worker-result.txt'
            final = 'completed: checked change; exact evidence includes `result.txt` and a trailing newline.\n'
            result.write_text(final, encoding='utf-8')
            roles = set()
            for example in examples:
                role = 'reviewer' if '--role reviewer' in example else 'executor'
                roles.add(role)
                assignment = root / f'{role}-assignment.txt'
                values = {'workflow-skill-directory': PACKAGE.as_posix(),
                          'absolute-workspace-root': root.as_posix(), 'unit': 'W-001/steps-1-2',
                          'own-agent-id': '/root/manager', 'project name': 'Änderung 中文',
                          'number': '9', 'class': 'low', 'facts.txt': facts.as_posix(),
                          'review-facts.txt': facts.as_posix(), 'worker-result.txt': result.as_posix(),
                          'new-absolute-assignment-file': assignment.as_posix()}
                for name, value in values.items():
                    example = example.replace('<' + name + '>', value)
                self.assertNotRegex(example, r'<[^>]+>')
                argv = shlex.split(example)
                built = subprocess.run([sys.executable, *argv[1:]], capture_output=True,
                                       text=True, encoding='utf-8')
                payload = self.consume(built)
                match = re.search(r'Read the complete UTF-8 assignment from (.*?) before any project work\.', payload['message'])
                self.assertIsNotNone(match)
                assignment = Path(match[1])
                self.addCleanup(assignment.unlink, missing_ok=True)
                self.assertFalse(assignment.is_relative_to(root))
                self.assertTrue(assignment.is_file(), 'The documented call must retain its full assignment in a file')
                delivered = assignment.read_text(encoding='utf-8')
                self.assertIn(body, delivered)
                if role == 'reviewer':
                    self.assertIn(final, delivered)
                self.assertIn(assignment.as_posix(), payload['message'].replace('\\', '/'))
                # The actual returned native arguments fit a bounded tool response,
                # while the separately read assignment retains the larger payload.
                self.assertLess(len(built.stdout.encode('utf-8')), 4096)
                self.assertGreater(len(delivered.encode('utf-8')), 12000)
            self.assertEqual(roles, {'executor', 'reviewer'})

    def run_builder(self, script, *arguments, auto_file=True):
        auto_assignment = None
        if script == 'build_manager_handoff.py' and '--assignment-file' not in arguments:
            report = Path(arguments[arguments.index('--report-file') + 1])
            auto_assignment = report.parent / f'manager-assignment-{uuid.uuid4().hex}.txt'
            arguments = (*arguments, '--assignment-file', auto_assignment)
        if (auto_file and script == 'build_dispatch_prompt.py'
                and '--format' in arguments and arguments[arguments.index('--format') + 1] == 'create'
                and not any(flag in arguments for flag in ('--assignment-file', '--context-handoff', '--predecessor-agent-id'))):
            project = Path(arguments[arguments.index('--project-root') + 1])
            auto_assignment = project / f'child-assignment-{uuid.uuid4().hex}.txt'
            arguments = (*arguments, '--assignment-file', auto_assignment)
        result = subprocess.run([sys.executable, str(PACKAGE / 'scripts' / script), *map(str, arguments)],
                              env={**os.environ, 'CODEX_THREAD_ID': ID}, capture_output=True,
                              text=True, encoding='utf-8')
        result.auto_assignment = auto_assignment
        return result

    def consume(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        # Bind the generated payload unchanged to the exposed native schema.
        # Live host dispatch is a separate integration check.
        def spawn_agent(*, task_name, message, fork_turns, model, reasoning_effort):
            self.assertRegex(task_name, r'^scoville_(executor|reviewer)_[0-9]+(?:_[0-9a-f]+)+$')
            self.assertEqual(fork_turns, 'none')
            self.assertEqual(model, 'gpt-6-sol')
            self.assertEqual(reasoning_effort, 'high')
            self.assertIn('manager_agent_id=/root/manager', message)
            self.assertNotIn('send_message_to_thread', message)
            self.assertNotIn('set_thread_archived', message)
        spawn_agent(**data)
        prompt = self.prompt(data)
        writing = (PACKAGE / 'references/writing.md').read_text(encoding='utf-8')
        self.assertEqual(1, prompt.count(writing))
        return data

    def prompt(self, data):
        """Read the exact assignment from the native message, as a child does."""
        match = re.search(r'Read the complete UTF-8 assignment from (.*?) before any (?:receipt or )?project work\.', data['message'])
        if match:
            assignment = Path(match[1])
            self.assertTrue(assignment.is_file(), str(assignment))
            return assignment.read_text(encoding='utf-8')
        return data['message']

    def test_automatic_assignment_paths_are_external_complete_and_unique(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project Ä 中文'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            request = root / 'request.txt'
            request.write_text('Start only this authorized fixture.', encoding='utf-8')
            report = self.create_report(root)
            commands = [
                ('build_dispatch_prompt.py', ['--project-root', root, '--format', 'create',
                 '--manager-agent-id', '/root/manager', '--project-name', 'Fixture', '--worker-number', '1',
                 '--model', 'gpt-6-sol', '--thinking', 'high', '--unit', 'W-001/step-1', '--role', 'executor']),
                ('build_manager_handoff.py', ['--mode', 'start', '--project-root', root, '--request-file', request,
                 '--runner-id', '/root/runner', '--project-name', 'Fixture', '--manager-number', '1',
                 '--report-file', report, '--model', 'gpt-6-sol', '--thinking', 'high']),
                ('build_manager_handoff.py', ['--mode', 'successor', '--predecessor-id', '/root/previous',
                 '--runner-id', '/root/runner', '--project-name', 'Fixture', '--manager-number', '2',
                 '--report-file', report, '--model', 'gpt-6-sol', '--thinking', 'high'])]
            external_temp = Path(directory) / "Research and Development before tests ü ' $()"
            external_temp.mkdir()
            env = dict(os.environ, TMPDIR=str(external_temp), TEMP=str(external_temp), TMP=str(external_temp))
            paths = []
            for script, args in commands:
                for repeat in range(2):
                    result = subprocess.run([sys.executable, str(PACKAGE / 'scripts' / script), *map(str,args)],
                                            capture_output=True, text=True, encoding='utf-8', env=env)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    native = json.loads(result.stdout)
                    self.assertEqual(set(native), {'task_name', 'message', 'fork_turns', 'model', 'reasoning_effort'})
                    match = re.search(r'assignment from (.+) before any (?:other )?project work', native['message'])
                    self.assertIsNotNone(match)
                    path = Path(match[1])
                    self.addCleanup(path.unlink, missing_ok=True)
                    self.assertTrue(path.is_absolute())
                    self.assertEqual(path.parent.resolve(), external_temp.resolve())
                    self.assertFalse(path.is_relative_to(root))
                    self.assertNotIn(path, paths)
                    paths.append(path)
                    received = path.read_text(encoding='utf-8')
                    self.assertTrue(received.strip())
                    self.assertEqual(path.read_bytes(), received.encode('utf-8'))
                    if script == 'build_manager_handoff.py':
                        if 'start' in args:
                            self.assertIn('Start only this authorized fixture.', received)
                        else:
                            self.assertIn('Predecessor: /root/previous', received)
                            self.assertIn('first send HANDOFF_REQUEST directly to /root/previous', native['message'])
                        self.assertLess(native['message'].index('wait for START'), native['message'].index('read the complete UTF-8'))
                    else:
                        self.assertIn('Work Item context', received)

    def test_atomic_publication_collision_failure_and_corrected_call(self):
        from unittest.mock import patch
        import native_task_arguments as native
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / 'assignment Ä 中文.txt'
            content = 'Complete assignment with Unicode Ä 中文.\n' * 100
            native.publish_assignment(target, content)
            self.assertEqual(target.read_bytes(), content.encode('utf-8'))
            with self.assertRaisesRegex(ValueError, 'already exists'):
                native.publish_assignment(target, 'Overwrite.')
            self.assertEqual(target.read_bytes(), content.encode('utf-8'))
            failed = root / 'failed.txt'
            with patch.object(native.os, 'link', side_effect=OSError('unsupported filesystem')):
                with self.assertRaisesRegex(ValueError, 'atomic hard links'):
                    native.publish_assignment(failed, content)
            self.assertFalse(failed.exists())
            self.assertEqual(list(root.glob('.scoville-assignment-*.tmp')), [])
            native.publish_assignment(failed, content)
            self.assertEqual(failed.read_bytes(), content.encode('utf-8'))
            partial = root / 'partial.txt'
            real_temporary = native.tempfile.NamedTemporaryFile
            class PartialWrite:
                def __init__(self, *args, **kwargs):
                    self.stream = real_temporary(*args, **kwargs)
                def __enter__(self):
                    self.stream.__enter__()
                    self.name = self.stream.name
                    return self
                def write(self, data):
                    self.stream.write(data[:10])
                    raise OSError('partial temporary write failed')
                def __exit__(self, *args):
                    return self.stream.__exit__(*args)
            with patch.object(native.tempfile, 'NamedTemporaryFile', PartialWrite):
                with self.assertRaisesRegex(ValueError, 'partial temporary write failed'):
                    native.publish_assignment(partial, content)
            self.assertFalse(partial.exists())
            self.assertEqual(list(root.glob('.scoville-assignment-*.tmp')), [])
            native.publish_assignment(partial, content)
            self.assertEqual(partial.read_bytes(), content.encode('utf-8'))
            with patch.object(native.tempfile, 'gettempdir', return_value=str(root)):
                with self.assertRaisesRegex(ValueError, 'outside the project'):
                    native.assignment_path(None, root)
            with self.assertRaisesRegex(ValueError, 'existing absolute directory'):
                native.assignment_path(Path('relative.txt'), root)

    def test_dispatch_titles_cover_full_units_review_and_correction(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            evidence = root / 'result.txt'
            evidence.write_text('completed: checked change; remaining work unchanged', encoding='utf-8')
            facts = root / 'review-facts.txt'
            facts.write_text('Initial review of the first Step against its Acceptance. No earlier assessments.', encoding='utf-8')
            common = ['--project-root', root, '--format', 'create', '--manager-agent-id', '/root/manager',
                      '--project-name', 'Änderung 中文', '--worker-number', '7', '--model', 'gpt-6-sol', '--thinking', 'high']
            whole = self.consume(self.run_builder('build_dispatch_prompt.py', *common, '--unit', 'W-001', '--role', 'executor'))
            self.assertIn('Assignment: SC-WRK-7: Änderung 中文 · PLAN-0001/W-001/steps-1-2', whole['message'])
            for role, extra, label in [('executor', [], 'SC-WRK'), ('reviewer', ['--executor-result', evidence, '--supplemental-context', facts], 'SC-REV'),
                                       ('executor', ['--reviewer-result', evidence], 'SC-WRK')]:
                result = self.consume(self.run_builder('build_dispatch_prompt.py', *common, '--unit', 'W-001/step-1', '--role', role, *extra))
                self.assertIn(f'Assignment: {label}-7: Änderung 中文 · PLAN-0001/W-001/step-1', self.prompt(result))
                self.assertRegex(result['task_name'], rf'^scoville_{role}_7_[0-9a-f]{{32}}$')
                # Packaged role policy and delivery gates, not live rollover proof.
                rules = (
                    ('rollover_pending does not stop or shorten your assignment',
                     'finish the current execution unit, review or repair, including required corrections and checks',
                     'Do not return context_handoff with unfinished assigned work merely because a threshold was crossed')
                    if role == 'reviewer' else
                    ('finish the bounded change already started',
                     'A lower later reading does not cancel it',
                     'A retained measured crossing authorizes executor context_handoff',
                     'Never transfer a partly written change or running operation'))
                for rule in rules:
                    self.assertIn(rule, self.prompt(result))
                if role == 'executor':
                    self.assertNotIn('rollover_pending does not stop or shorten your assignment', self.prompt(result))
                    self.assertIn('Use completed when your assigned execution unit and checks are finished', self.prompt(result))
                    self.assertIn('even if manager review or Plan closure remains', self.prompt(result))
                    self.assertIn('work or required checks remaining within the current execution unit', self.prompt(result))
                self.assertIn(str((PACKAGE.parent / 'scoville-code' / 'SKILL.md').resolve()), self.prompt(result))
                self.assertTrue((PACKAGE.parent / 'scoville-code' / 'SKILL.md').is_file())
                self.assertIn('Treat a user stop as immediate', self.prompt(result))
                self.assertNotIn('On context_handoff, state finished Steps', self.prompt(result))
            invalid = self.run_builder('build_dispatch_prompt.py', *common, '--unit', 'W-001/step-1', '--role', 'reviewer')
            self.assertNotEqual(invalid.returncode, 0)
            self.assertEqual(invalid.stdout, '')
            self.assertIn('usage:', invalid.stderr)
            self.assertIn('--executor-result', invalid.stderr)

    def test_repeated_reviews_of_one_worker_spawn_with_distinct_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            evidence = root / 'result.txt'
            evidence.write_text('progress_pending: first Step checked; second Step remains', encoding='utf-8')
            facts = root / 'review-facts.txt'
            facts.write_text('Initial review of the checked first Step against its Acceptance. No earlier assessments.', encoding='utf-8')
            arguments = ['--project-root', root, '--format', 'create', '--manager-agent-id', '/root/manager',
                         '--project-name', 'fixture', '--worker-number', '2', '--model', 'gpt-6-sol',
                         '--thinking', 'high', '--unit', 'W-001/step-1', '--role', 'reviewer',
                         '--executor-result', evidence, '--supplemental-context', facts]
            assigned = set()
            payloads = []
            for _ in range(2):
                payload = self.consume(self.run_builder('build_dispatch_prompt.py', *arguments))
                self.assertNotIn(payload['task_name'], assigned, 'Native task name already assigned')
                assigned.add(payload['task_name'])
                payloads.append(payload)
            self.assertEqual({k: v for k, v in payloads[0].items() if k not in ('task_name', 'message')},
                             {k: v for k, v in payloads[1].items() if k not in ('task_name', 'message')})
            self.assertEqual(self.prompt(payloads[0]), self.prompt(payloads[1]))

    def test_generated_checkpoint_runs_unchanged_in_host_shell(self):
        shell = shutil.which('pwsh') or shutil.which('powershell') if os.name == 'nt' else shutil.which('sh')
        if not shell:
            self.skipTest('Host shell unavailable; checkpoint command consumer remains unverified')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "project's $value"
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            result_file = root / 'result.txt'
            result_file.write_text('completed: assigned fixture checked', encoding='utf-8')
            facts = root / 'review-facts.txt'
            facts.write_text('Initial review of the first Step fixture against its Acceptance. No earlier assessments.', encoding='utf-8')
            environment = {**os.environ, 'CODEX_THREAD_ID': ID}
            for role in ('executor', 'reviewer'):
                extra = ['--executor-result', result_file, '--supplemental-context', facts] if role == 'reviewer' else []
                payload = self.consume(self.run_builder('build_dispatch_prompt.py',
                    '--project-root', root, '--unit', 'W-001/step-1', '--role', role,
                    '--format', 'create', '--manager-agent-id', '/root/manager',
                    '--project-name', 'fixture', '--worker-number', '1',
                    '--model', 'gpt-6-sol', '--thinking', 'high', *extra))
                commands = [line for line in self.prompt(payload).splitlines()
                            if 'check_context_checkpoint.py' in line]
                self.assertEqual(len(commands), 1)
                invocation = ([shell, '-NoProfile', '-NonInteractive', '-Command', commands[0]]
                              if os.name == 'nt' else [shell, '-c', commands[0]])
                result = subprocess.run(invocation, env=environment, capture_output=True,
                                        text=True, encoding='utf-8')
                self.assertEqual(result.returncode, 0, result.stderr)
                checkpoint = json.loads(result.stdout)
                self.assertEqual(checkpoint['role'], role)
                self.assertEqual(checkpoint['thread_id'], ID)
                config = root / '.scoville/config.json'
                config.parent.mkdir(exist_ok=True)
                config.write_text(json.dumps({'workflow': {'context': {'worker_percent': 'invalid'}}}), encoding='utf-8')
                invalid = subprocess.run(invocation, env=environment, capture_output=True,
                                         text=True, encoding='utf-8')
                self.assertNotEqual(invalid.returncode, 0)
                self.assertEqual(json.loads(invalid.stdout)['reason'], 'configuration_invalid')
                config.unlink()

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
            self.assertIn(str(code.resolve()), assignment.read_text(encoding='utf-8'))
            self.assertEqual(code.read_bytes(), content)

    def test_prior_code_fix_pauses_and_resumes_the_full_group_after_review(self):
        # Contract coverage through the packaged CLI and native argument consumer;
        # actual agent pause/resume and measured rollover remain live acceptance.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            facts, result = root / 'facts.txt', root / 'result.txt'
            facts.write_text('Assigned group: fix previously checked product code if needed, then finish dependent tests. '
                             'rollover_pending was measured before the fix; hand over remaining work after review.', encoding='utf-8')
            common = ['--project-root', root, '--format', 'create', '--manager-agent-id', '/root/manager',
                      '--project-name', 'Fixture', '--model', 'gpt-6-sol', '--thinking', 'high',
                      '--unit', 'W-001/steps-1-2', '--supplemental-context', facts]
            worker = self.consume(self.run_builder('build_dispatch_prompt.py', *common,
                                  '--role', 'executor', '--worker-number', '7'))
            for rule in ('return review_pending', 'including after rollover_pending',
                         'This pauses the same assignment', 'only after the manager confirms review acceptance',
                         'or review acceptance', 'completed, review_pending, blocked'):
                self.assertIn(rule, self.prompt(worker))
            self.assertIn('include the full continuation facts below', self.prompt(worker))
            self.assertIn("manager's fresh successor after review acceptance", self.prompt(worker))
            self.assertNotIn('completes your assignment after focused checks', self.prompt(worker))
            self.assertIn('W-001/steps-1-2', self.prompt(worker))
            paused = 'review_pending: prior-code fix checked; dependent tests remain. Retained rollover_pending: 61/100 percent.'
            result.write_text(paused, encoding='utf-8')
            review = self.consume(self.run_builder('build_dispatch_prompt.py', *common,
                                  '--role', 'reviewer', '--worker-number', '7', '--executor-result', result))
            self.assertIn(paused, self.prompt(review))
            self.assertIn('scoville_role=reviewer', self.prompt(review).splitlines())
            self.assertTrue(review['task_name'].startswith('scoville_reviewer_7_'))
            self.assertNotIn('completed, review_pending, blocked', self.prompt(review))
            finding = 'changes_requested: the checked fix misses rollback; correct rollback before dependent tests resume.'
            result.write_text(finding, encoding='utf-8')
            repair = self.consume(self.run_builder('build_dispatch_prompt.py', *common,
                                  '--role', 'executor', '--worker-number', '8', '--reviewer-result', result))
            self.assertIn(finding, self.prompt(repair))
            self.assertNotEqual(worker['task_name'], repair['task_name'])
            handoff = root / 'handoff.txt'
            handoff.write_text(paused, encoding='utf-8')
            facts.write_text('Review accepted; rollback correction checked. Only dependent tests remain. '
                             'Preserve prior effects and checks. Acceptance: all dependent tests pass.', encoding='utf-8')
            successor = self.consume(self.run_builder('build_dispatch_prompt.py', *common,
                '--role', 'executor', '--worker-number', '9', '--context-handoff', handoff,
                '--predecessor-agent-id', '/root/worker7'))
            delivered = self.prompt(successor)
            self.assertTrue(delivered.startswith('FIRST ACTION'))
            self.assertIn('HANDOFF_ACCEPTED /root/worker7', delivered)
            self.assertIn('TAKEOVER_COMPLETE', delivered)
            self.assertIn(paused, delivered)
            self.assertIn(facts.read_text(encoding='utf-8'), delivered)
            self.assertNotIn('## Work Item context', delivered)
            # Manager review cadence is verified in native Workflow cases.
            # Rewording its instructions is not an exact-prose acceptance gate.

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
                    self.assertEqual(assignment.read_bytes(), self.prompt(full).encode('utf-8'))
                    self.assertIn(body, assignment.read_text(encoding='utf-8'))
                    writing = (PACKAGE / 'references/writing.md').read_text(encoding='utf-8')
                    self.assertEqual(1, assignment.read_text(encoding='utf-8').count(writing))
                    self.assertIn(str(assignment), short['message'])
                    self.assertNotIn(body, short['message'])
                    self.assertEqual({k: v for k, v in full.items() if k not in ('message', 'task_name')},
                                     {k: v for k, v in short.items() if k not in ('message', 'task_name')})
                    self.assertNotEqual(full['task_name'], short['task_name'])
                    self.assertIn(f'scoville_role={role}', assignment.read_text(encoding='utf-8').splitlines())
                    for generated in (full, short):
                        self.assertTrue(generated['task_name'].startswith(f'scoville_{role}_9_'))

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
                     (['--format', 'prompt', '--assignment-file', root / 'text.txt'], '--assignment-file requires --format create'),
                     (['--predecessor-agent-id', '/root/old', '--assignment-file', root / 'recovery.txt'], '--predecessor-agent-id requires --context-handoff and --supplemental-context')]
            before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            for extra, diagnostic in cases:
                with self.subTest(extra=extra):
                    invocation = common
                    if '--format' in extra and extra[extra.index('--format') + 1] == 'prompt':
                        invocation = ['--project-root', root, '--manager-agent-id', '/root/manager',
                                      '--unit', 'W-001/step-1', '--role', 'executor']
                    failed = self.run_builder('build_dispatch_prompt.py', *invocation, *extra, auto_file=False)
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
                    assignment = self.prompt(result)
                    self.assertTrue(assignment.startswith('FIRST ACTION'))
                    self.assertIn('target=/root/manager and message=HANDOFF_ACCEPTED ' + predecessor, assignment)
                    self.assertNotIn('target=' + predecessor, assignment)
                    self.assertNotIn('## Work Item context', assignment)
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
        auto_assignment = getattr(result, 'auto_assignment', None)
        if auto_assignment is not None:
            self.assertIn(str(auto_assignment), data['message'])
            assignment = auto_assignment.read_text(encoding='utf-8')
            self.assertNotIn(assignment, data['message'])
            data['message'] = assignment
        return data

    def test_manager_start_and_successor_have_separate_context(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = root / 'request.txt'
            body = 'Start Scoville Workflow for the active Plan. Internal coordination authorized.'
            request.write_text(body, encoding='utf-8')
            report = self.create_report(root)
            common = ['--runner-id', '/root', '--project-name', 'Test 中文', '--manager-number', '1', '--report-file', report]
            start = self.consume_manager(self.run_builder('build_manager_handoff.py', *common,
                '--mode', 'start', '--project-root', root, '--request-file', request))
            self.assertRegex(start['task_name'], r'^scoville_manager_1_[0-9a-f]{32}$')
            self.assertIn(body, start['message'])
            self.assertIn(str(root), start['message'])
            self.assertEqual(start['model'], 'gpt-6.1-sol')
            self.assertEqual(start['reasoning_effort'], 'high')
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
                self.assertIn('Project display name: Test 中文.', data['message'])
                self.assertRegex(data['message'], r'[Ss]end READY')
                self.assertIn('for START from that exact host sender', data['message'])
                self.assertIn('including in your final answer', data['message'])
                protocol = PACKAGE / 'references/manager-protocol.md'
                self.assertIn(str(protocol.resolve()), data['message'])
                self.assertTrue(protocol.is_file())
                writing = PACKAGE / 'references/writing.md'
                self.assertIn(str(writing.resolve()), data['message'])
                self.assertIn('read after START before writing', data['message'])
                self.assertTrue(writing.read_text(encoding='utf-8').strip())

    def test_manager_assignment_file_delivers_complete_prompt_without_path_copying(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project with spaces'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            request = root / 'request.txt'
            activation = 'Start PLAN-0001. Preserve this long technical scope: ' + 'Ä / x\\y `z` ' * 300
            request.write_text(activation, encoding='utf-8')
            report = self.create_report(root)
            common = ['--runner-id', '/root/runner', '--project-name', 'Test 中文',
                      '--report-file', report, '--model', 'gpt-6-luna', '--thinking', 'high']
            start_file = root / 'manager start.txt'
            start_args = [*common, '--manager-number', '1', '--mode', 'start',
                          '--project-root', root, '--request-file', request,
                          '--assignment-file', start_file]
            start = self.consume_manager(self.run_builder('build_manager_handoff.py', *start_args))
            self.assertIn(str(start_file), start['message'])
            self.assertIn('Your commentary is not addressed to the user.', start['message'])
            self.assertLess(start['message'].index('minimal labelled fields'), start['message'].index('## Manager entry'))
            self.assertIn('minimal labelled fields', start_file.read_text(encoding='utf-8'))
            self.assertIn(str((PACKAGE / 'references/manager-protocol.md').resolve()), start['message'])
            self.assertNotIn(activation, start['message'])
            full_start = start_file.read_text(encoding='utf-8')
            self.assertIn(activation.rstrip(), full_start)
            self.assertIn(str((PACKAGE / 'references/operations.md').resolve()), full_start)
            self.assertIn(str((PACKAGE.parent / 'scoville-plan/SKILL.md').resolve()), full_start)
            self.assertIn(str(report), full_start)
            failed = self.run_builder('build_manager_handoff.py', *start_args)
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(failed.stdout, '')
            self.assertIn('--assignment-file already exists', failed.stderr)
            successor_file = root / 'manager successor.txt'
            successor = self.consume_manager(self.run_builder('build_manager_handoff.py',
                *common, '--manager-number', '2', '--mode', 'successor',
                '--predecessor-id', '/root/old', '--assignment-file', successor_file))
            self.assertIn('first send HANDOFF_REQUEST directly to /root/old', successor['message'])
            self.assertIn(str(successor_file), successor['message'])
            self.assertIn('Your commentary is not addressed to the user.', successor['message'])
            self.assertLess(successor['message'].index('minimal labelled fields'), successor['message'].index('## Manager entry'))
            full_successor = successor_file.read_text(encoding='utf-8')
            self.assertIn('minimal labelled fields', full_successor)
            self.assertIn('before writing free-text commentary, messages', full_successor)
            self.assertIn('Predecessor: /root/old', full_successor)
            self.assertNotIn(activation, full_successor)
            self.assertIn(str(report), full_successor)

    def test_manager_builder_without_required_request_has_no_payload(self):
        failed = subprocess.run([sys.executable, str(PACKAGE / 'scripts/build_manager_handoff.py'),
                                 '--mode', 'start', '--runner-id', '/root', '--project-name', 'Fixture',
                                 '--manager-number', '1'], capture_output=True, text=True, encoding='utf-8')
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(failed.stdout, '')
        self.assertIn('--mode start requires --project-root', failed.stderr)

    def test_missing_writing_rules_fail_then_corrected_helpers_feed_consumers(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            copy = base / 'suite' / PACKAGE.name
            shutil.copytree(PACKAGE, copy)
            shutil.copytree(PACKAGE.parent / 'scoville-code', copy.parent / 'scoville-code')
            shutil.copytree(PACKAGE.parent / 'scoville-plan', copy.parent / 'scoville-plan')
            writing = copy / 'references/writing.md'
            original = writing.read_bytes()
            request = root / 'request.txt'
            request.write_text('Start the explicitly scoped fixture Workflow.', encoding='utf-8')
            report = self.create_report(root)
            calls = [
                ('build_dispatch_prompt.py', ['--project-root', root, '--format', 'create',
                 '--manager-agent-id', '/root/manager', '--project-name', 'Fixture',
                 '--worker-number', '1', '--model', 'gpt-6-sol', '--thinking', 'high',
                 '--unit', 'W-001/step-1', '--role', 'executor',
                 '--assignment-file', root / 'worker-assignment.txt']),
                ('build_manager_handoff.py', ['--mode', 'start', '--project-root', root,
                 '--request-file', request, '--runner-id', '/root', '--project-name', 'Fixture',
                 '--manager-number', '1', '--report-file', report,
                 '--assignment-file', root / 'manager-assignment.txt']),
            ]
            for script, args in calls:
                command = [sys.executable, str(copy / 'scripts' / script), *map(str, args)]
                writing.unlink()
                failed = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
                self.assertNotEqual(0, failed.returncode)
                self.assertEqual('', failed.stdout)
                self.assertIn('writing.md', failed.stderr)
                self.assertIn('intact matching suite package', failed.stderr)
                writing.write_bytes(original)
                corrected = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
                if script == 'build_dispatch_prompt.py':
                    self.consume(corrected)
                else:
                    result = self.consume_manager(corrected)
                    self.assertIn(str(root / 'manager-assignment.txt'), result['message'])
                    self.assertIn(str(writing.resolve()), (root / 'manager-assignment.txt').read_text(encoding='utf-8'))
                    self.assertEqual(original, writing.read_bytes())

    def test_dispatch_conditional_shell_reference_is_required_and_absolute(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            copy = base / 'suite' / PACKAGE.name
            shutil.copytree(PACKAGE, copy)
            shutil.copytree(PACKAGE.parent / 'scoville-code', copy.parent / 'scoville-code')
            shutil.copytree(PACKAGE.parent / 'scoville-plan', copy.parent / 'scoville-plan')
            shell = copy / 'references/shell-commands.md'
            original = shell.read_bytes()
            shell.unlink()
            assignment = root / 'assignment.txt'
            command = [sys.executable, str(copy / 'scripts/build_dispatch_prompt.py'),
                       '--project-root', str(root), '--format', 'create',
                       '--manager-agent-id', '/root/manager', '--project-name', 'Fixture',
                       '--worker-number', '1', '--model', 'gpt-6-sol', '--thinking', 'high',
                       '--unit', 'W-001/step-1', '--role', 'executor',
                       '--assignment-file', str(assignment)]
            failed = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            self.assertNotEqual(0, failed.returncode)
            self.assertEqual('', failed.stdout)
            self.assertFalse(assignment.exists())
            self.assertIn(str(shell.resolve()), failed.stderr)
            shell.write_bytes(original)
            corrected = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            self.consume(corrected)
            prompt = assignment.read_text(encoding='utf-8')
            self.assertIn(f'shell_command_rules: {shell.resolve()}; read before the first shell command.', prompt)
            self.assertNotIn(shell.read_text(encoding='utf-8'), prompt)

    def test_manager_plan_paths_feed_real_plan_consumers_in_both_layouts(self):
        for wrapped in (False, True):
            with self.subTest(wrapped=wrapped), tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                project = base / 'project'
                shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', project)
                suite = base / 'suite'
                for name in ('scoville-plan', 'scoville-workflow-for-codex'):
                    target = suite / name / name if wrapped else suite / name
                    shutil.copytree(PACKAGE.parent / name, target)
                workflow = suite / PACKAGE.name / PACKAGE.name if wrapped else suite / PACKAGE.name
                plan = suite / 'scoville-plan' / 'scoville-plan' if wrapped else suite / 'scoville-plan'
                request = project / 'request.txt'
                request.write_text('Start the authorized fixture Workflow.', encoding='utf-8')
                report = self.create_report(project)
                command = [sys.executable, str(workflow / 'scripts/build_manager_handoff.py'),
                           '--runner-id', '/root', '--project-name', 'fixture', '--manager-number', '1',
                           '--report-file', str(report), '--model', 'gpt-6-luna', '--thinking', 'high']
                for mode, extra in [('start', ['--project-root', str(project), '--request-file', str(request)]),
                                    ('successor', ['--predecessor-id', '/root/manager1'])]:
                    assignment_path = project / f'manager-{mode}-assignment.txt'
                    invocation = command + ['--mode', mode, '--assignment-file', str(assignment_path)] + extra
                    entrypoint = plan / 'SKILL.md'
                    content = entrypoint.read_bytes()
                    entrypoint.unlink()
                    failed = subprocess.run(invocation, capture_output=True, text=True, encoding='utf-8')
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertEqual(failed.stdout, '')
                    self.assertIn(str(entrypoint.resolve()), failed.stderr)
                    self.assertIn('complete matching suite package', failed.stderr)
                    entrypoint.write_bytes(content)
                    result = subprocess.run(invocation, capture_output=True, text=True, encoding='utf-8')
                    assignment = self.consume_manager(result)
                    self.assertIn(str(assignment_path), assignment['message'])
                    paths = [line.removeprefix('Plan Skill: ') for line in assignment_path.read_text(encoding='utf-8').splitlines()
                             if line.startswith('Plan Skill: ')]
                    self.assertEqual(len(paths), 1)
                    actual = Path(paths[0])
                    self.assertEqual(actual.read_bytes(), content)
                    selected = subprocess.run([sys.executable, str(actual.parent / 'scripts/select_context.py'),
                        '--root', str(project), '--unit', 'W-001/step-1', '--format', 'json'],
                        capture_output=True, text=True, encoding='utf-8')
                    self.assertEqual(selected.returncode, 0, selected.stdout + selected.stderr)
                    self.assertEqual(json.loads(selected.stdout)['work_item']['unit'], 'W-001/step-1')
                    validated = subprocess.run([sys.executable, str(actual.parent / 'scripts/validate_profile.py'),
                        '--root', str(project), '--format', 'json'], capture_output=True, text=True, encoding='utf-8')
                    self.assertEqual(validated.returncode, 0, validated.stdout + validated.stderr)
                    self.assertTrue(json.loads(validated.stdout)['valid'])

    def test_manager_invalid_calls_then_corrected_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            request = root / 'request.txt'
            request.write_text('Start Scoville Workflow.', encoding='utf-8')
            report = self.create_report(root)
            common = ['--runner-id', '/root', '--project-name', 'Test', '--manager-number', '2', '--report-file', report]
            successor = ['--mode', 'successor', '--predecessor-id', 'old-manager',
                         '--model', 'gpt-6.1-sol', '--thinking', 'medium']
            cases = [
                (['--mode', 'successor'], '--predecessor-id', successor),
                (successor + ['--request-file', request], 'omit --request-file', successor),
                (successor + ['--project-root', root], 'omit --request-file', successor),
                (['--mode', 'successor', '--predecessor-id', 'old-manager', '--model', 'gpt-6-astra'], 'both --model and --thinking',
                 successor + ['--model', 'gpt-6-astra', '--thinking', 'high']),
                (['--mode', 'successor', '--predecessor-id', 'old-manager'], 'launched pair', successor),
                (['--mode', 'successor', '--predecessor-id', '/root'], 'not --runner-id', successor),
                (['--mode', 'start'], '--project-root',
                 ['--mode', 'start', '--project-root', root, '--request-file', request]),
                (['--mode', 'start', '--project-root', root], '--request-file',
                 ['--mode', 'start', '--project-root', root, '--request-file', request]),
                (successor + ['--manager-number', '0'], 'positive integer', successor),
                (successor + ['--runner-id', 'bad\nID'], '--runner-id', successor),
                (successor + ['--project-name', 'bad\nName'], '--project-name', successor),
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
            common = ['--runner-id', '/root', '--project-name', 'Test', '--manager-number', '1', '--report-file', report, '--mode', 'start',
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
            common = ['--runner-id', '/root', '--project-name', 'Test', '--manager-number', '2', '--mode', 'successor', '--report-file', report]
            for identity in ('', '  ', 'old\nother', 'old\rother'):
                with self.subTest(identity=identity):
                    failed = self.run_builder('build_manager_handoff.py', *common,
                                              '--predecessor-id', identity)
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertEqual(failed.stdout, '')
                    self.assertIn('--predecessor-id', failed.stderr)
                    self.assertIn('usage:', failed.stderr)
            self.consume_manager(self.run_builder('build_manager_handoff.py', *common,
                                 '--predecessor-id', '/root/old_manager',
                                 '--model', 'gpt-6.1-sol', '--thinking', 'medium'))

    def test_runner_and_report_stay_bound_to_each_project(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            runs = []
            for name in ('fluid', 'empco'):
                root = base / name
                shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
                request = root / 'request.txt'
                request.write_text('Start Workflow for PLAN-0001.', encoding='utf-8')
                report = self.create_report(root)
                runner = '/root/' + name
                common = ['--runner-id', runner, '--project-name', name, '--manager-number', '1', '--report-file', report]
                start = self.consume_manager(self.run_builder('build_manager_handoff.py', *common,
                    '--mode', 'start', '--project-root', root, '--request-file', request))
                successor = self.consume_manager(self.run_builder('build_manager_handoff.py', *common,
                    '--mode', 'successor', '--predecessor-id', runner + '/manager',
                    '--model', start['model'], '--thinking', start['reasoning_effort']))
                for data in (start, successor):
                    self.assertIn('Project display name: ' + name + '.', data['message'])
                    self.assertIn('Runner agent: ' + runner + '.', data['message'])
                    self.assertIn('Run report (same file for all managers): ' + str(report), data['message'])
                    self.assertNotIn('/root/' + ('empco' if name == 'fluid' else 'fluid'), data['message'])
                child_result = self.run_builder('build_dispatch_prompt.py', '--project-root', root,
                    '--unit', 'W-001', '--role', 'executor', '--format', 'create',
                    '--manager-agent-id', runner + '/manager', '--project-name', name,
                    '--worker-number', '1', '--model', 'gpt-6-luna', '--thinking', 'medium')
                self.assertEqual(child_result.returncode, 0, child_result.stderr)
                child = json.loads(child_result.stdout)
                self.assertIn('manager_agent_id=' + runner + '/manager', child['message'])
                self.assertIn('Do not write the report or message the runner.', self.prompt(child))
                self.assertNotIn('/root/' + ('empco' if name == 'fluid' else 'fluid'), child['message'])
                runs.append((root, request, report, common))
            root, request, _, common = runs[0]
            failed = self.run_builder('build_manager_handoff.py', *common, '--report-file', runs[1][2],
                '--mode', 'start', '--project-root', root, '--request-file', request)
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(failed.stdout, '')
            self.assertIn('this project', failed.stderr)

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
            assignment = self.prompt(result)
            self.assertIn('A passed. Only B remains.', assignment)
            self.assertIn('No commits. Check B only.', assignment)


if __name__ == '__main__':
    unittest.main()
