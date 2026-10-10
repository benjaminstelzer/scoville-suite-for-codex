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

    def test_explorer_question_needs_no_plan_and_rejects_execution_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            facts = root / 'question.txt'
            facts.write_text('Question: Ä 中文 — "Wer besitzt dieses Verhalten?" No external access.', encoding='utf-8')
            base = ['--project-root', root, '--role', 'explorer', '--manager-agent-id', '/root/manager',
                    '--format', 'create', '--project-name', 'Fixture', '--worker-number', '1',
                    '--model', 'gpt-6-sol', '--thinking', 'high']
            failed = self.run_builder('build_dispatch_prompt.py', *base)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('complete question', failed.stderr)
            failed = self.run_builder('build_dispatch_prompt.py', *base,
                                      '--supplemental-context', facts, '--executor-result', facts)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn('no executor or reviewer result flags', failed.stderr)
            result = self.run_builder('build_dispatch_prompt.py', *base, '--supplemental-context', facts)
            payload = self.consume(result)
            prompt = self.prompt(payload)
            for text in (payload['message'], prompt):
                self.assertIn('Use English for internal commentary, messages and results.', text)
                self.assertIn('keep quotes, relay text and literals exact.', text)
            self.assertIn(facts.read_text(encoding='utf-8'), prompt)
            self.assertIn('do not implement, change project files, run tests', prompt)
            self.assertIn('Do not claim review acceptance', prompt)
            self.assertIn('SC-EXP-1:', prompt)
            self.assertFalse((root / 'PROJECT_INDEX.md').exists())

    def test_explorer_optional_plan_unit_keeps_identity_and_context(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            facts = Path(directory) / 'question.txt'
            facts.write_text('Question: identify the owner for this Step. Read-only.', encoding='utf-8')
            result = self.run_builder('build_dispatch_prompt.py', '--project-root', root,
                '--role', 'explorer', '--unit', 'W-001/step-1', '--manager-agent-id', '/root/manager',
                '--format', 'create', '--project-name', 'Fixture', '--worker-number', '1',
                '--model', 'gpt-6-sol', '--thinking', 'high', '--supplemental-context', facts)
            prompt = self.prompt(self.consume(result))
            self.assertIn('## Non-goals', prompt)
            self.assertIn('## Work Item context', prompt)
            self.assertIn('SC-EXP-1: Fixture · PLAN-0001/W-001/step-1', prompt)

    def test_role_input_failures_then_literal_safe_complete_consumer(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'project Ä 中文'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            facts = base / 'facts.txt'
            facts.write_text('Review only this assigned unit. No commits.', encoding='utf-8')
            for flag, role in [('--executor-result', 'reviewer'), ('--reviewer-result', 'executor'),
                               ('--supplemental-context', 'executor')]:
                with self.subTest(flag=flag):
                    source = base / (flag[2:] + ' Ä 中文.txt')
                    assignment = base / (flag[2:] + '-assignment.txt')
                    arguments = ['--project-root', root, '--format', 'create', '--project-name', 'Fixture',
                        '--worker-number', '1', '--model', 'gpt-6-sol', '--thinking', 'high',
                        '--unit', 'W-001/step-1', '--role', role, '--manager-agent-id', '/root/manager',
                        '--assignment-file', assignment, flag, source]
                    if flag != '--supplemental-context':
                        arguments.extend(['--supplemental-context', facts])
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
        self.assertEqual(len(examples), 3)
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
                role = re.search(r'--role (\w+)', example)[1]
                roles.add(role)
                assignment = root / f'{role}-assignment.txt'
                values = {'workflow-skill-directory': PACKAGE.as_posix(),
                          'absolute-workspace-root': root.as_posix(), 'unit': 'W-001/steps-1-2',
                          'own-agent-id': '/root/manager', 'project name': 'Änderung 中文',
                          'number': '9', 'class': 'low', 'facts.txt': facts.as_posix(),
                          'review-facts.txt': facts.as_posix(), 'worker-result.txt': result.as_posix(),
                          'new-absolute-assignment-file': assignment.as_posix()}
                values.update({'explorer-number': '9', 'question-and-facts.txt': facts.as_posix()})
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
            self.assertEqual(roles, {'executor', 'reviewer', 'explorer'})

    def run_builder(self, script, *arguments, auto_file=True):
        auto_assignment = None
        if (auto_file and script == 'build_dispatch_prompt.py'
                and '--format' in arguments and arguments[arguments.index('--format') + 1] == 'create'
                and '--assignment-file' not in arguments):
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
            self.assertRegex(task_name, r'^scoville_(executor|reviewer|explorer)_[0-9]+(?:_[0-9a-f]+)+$')
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
            commands = [
                ('build_dispatch_prompt.py', ['--project-root', root, '--format', 'create',
                 '--manager-agent-id', '/root/manager', '--project-name', 'Fixture', '--worker-number', '1',
                 '--model', 'gpt-6-sol', '--thinking', 'high', '--unit', 'W-001/step-1', '--role', 'executor'])]
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
                for text in (result['message'], self.prompt(result)):
                    self.assertIn('Use English for internal commentary, messages and results.', text)
                    self.assertIn('keep quotes, relay text and literals exact.', text)
                self.assertIn(f'Assignment: {label}-7: Änderung 中文 · PLAN-0001/W-001/step-1', self.prompt(result))
                self.assertRegex(result['task_name'], rf'^scoville_{role}_7_[0-9a-f]{{32}}$')
                for obsolete in ('rollover_pending', 'context_handoff', 'check_context_checkpoint', 'TAKEOVER_COMPLETE', 'progress_pending', 'broader assignment'):
                    self.assertNotIn(obsolete, self.prompt(result))
                if role == 'executor':
                    self.assertIn('Use completed when your assigned execution unit and checks are finished', self.prompt(result))
                self.assertIn(f'suite_directory: {PACKAGE.parent.resolve()}', self.prompt(result))
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
            evidence.write_text('completed: assigned first Step checked; second Step unreleased', encoding='utf-8')
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


    def test_wrapped_release_dispatch_does_not_require_an_unselected_skill(self):
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
            without_code = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            self.consume(without_code)
            delivered = assignment.read_text(encoding='utf-8')
            self.assertIn(f'suite_directory: {(base / "packages").resolve()}', delivered)
            self.assertNotIn(str(code.resolve()), delivered)
            code.write_bytes(content)
            assignment = project / 'assignment-with-code.txt'
            command[-1] = str(assignment)
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            self.consume(result)
            self.assertIn(f'suite_directory: {(base / "packages").resolve()}', assignment.read_text(encoding='utf-8'))
            self.assertEqual(code.read_bytes(), content)

    def test_required_early_review_preserves_same_assignment_contract(self):
        # Contract coverage through the packaged CLI and native argument consumer;
        # actual agent pause/resume remains live acceptance.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
            facts, result = root / 'facts.txt', root / 'result.txt'
            facts.write_text('Assigned group: finish the coherent product fix and focused checks. '
                             'Review acceptance is required before the costly migration gate. '
                             'Keep the current executor paused during independent review.', encoding='utf-8')
            common = ['--project-root', root, '--format', 'create', '--manager-agent-id', '/root/manager',
                      '--project-name', 'Fixture', '--model', 'gpt-6-sol', '--thinking', 'high',
                      '--unit', 'W-001/steps-1-2', '--supplemental-context', facts]
            worker = self.consume(self.run_builder('build_dispatch_prompt.py', *common,
                                  '--role', 'executor', '--worker-number', '7'))
            for rule in ('Return review_pending',
                         'This pauses the same assignment', 'only after the manager confirms review acceptance',
                         'or review acceptance', 'completed, review_pending, blocked'):
                self.assertIn(rule, self.prompt(worker))
            self.assertNotIn('completes your assignment after focused checks', self.prompt(worker))
            self.assertIn('W-001/steps-1-2', self.prompt(worker))
            paused = 'review_pending: coherent fix checked; costly migration gate requires review acceptance.'
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
            self.assertNotIn('TAKEOVER_COMPLETE', self.prompt(repair))

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
                     (['--predecessor-agent-id', '/root/old', '--assignment-file', root / 'recovery.txt'], 'unrecognized arguments: --predecessor-agent-id')]
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
            calls = [
                ('build_dispatch_prompt.py', ['--project-root', root, '--format', 'create',
                 '--manager-agent-id', '/root/manager', '--project-name', 'Fixture',
                 '--worker-number', '1', '--model', 'gpt-6-sol', '--thinking', 'high',
                 '--unit', 'W-001/step-1', '--role', 'executor',
                 '--assignment-file', root / 'worker-assignment.txt']),
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
                self.consume(corrected)
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
            self.assertIn(f'shell_command_rules: {shell.resolve()}; read before shell commands, complete-file preparation or output that may exceed an applicable limit.', prompt)
            self.assertNotIn(shell.read_text(encoding='utf-8'), prompt)








if __name__ == '__main__':
    unittest.main()
