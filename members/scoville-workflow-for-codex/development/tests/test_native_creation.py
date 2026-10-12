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

from test_contract import PACKAGE, SUITE_ROOT, _builder, _config, copy_started_profile

ID = '01a0e778-0c80-7660-b8b9-c8ce59a9fed4'


class NativeCreationTests(unittest.TestCase):

    def test_explicit_language_reaches_native_and_prompt_consumers_for_every_role(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            evidence = root / 'literal-input.txt'
            original = 'status: done\nOriginal quote: "Keep English"; café 中文; `owner.py`.\n'
            evidence.write_bytes(original.encode('utf-8'))
            for role in ('explorer', 'executor', 'reviewer'):
                role_args = (['--supplemental-context', evidence] if role == 'explorer' else
                             ['--executor-result', evidence] if role == 'reviewer' else
                             ['--reviewer-result', evidence])
                for language in ('German', 'English'):
                    with self.subTest(role=role, language=language):
                        args = ['--project-root', root, '--unit', 'W-001/step-1', '--role', role,
                                '--communication-language', language, *role_args]
                        before = {p:p.read_bytes() for p in root.rglob('*') if p.is_file()}
                        direct = self.run_builder('build_dispatch_prompt.py', *args, '--format', 'prompt')
                        self.assertEqual(direct.returncode, 0, direct.stderr)
                        self.assertEqual(before, {p:p.read_bytes() for p in root.rglob('*') if p.is_file()})
                        created = self.consume(self.run_builder('build_dispatch_prompt.py', *args,
                            '--format', 'create', '--project-name', 'Fixture', '--worker-number', '1',
                            '--model', 'gpt-6-sol', '--thinking', 'high'))
                        complete = self.prompt(created)
                        self.assertTrue(complete.startswith(direct.stdout))
                        for received in (direct.stdout, created['message'], complete):
                            self.assertIn(f'Communication language: {language}.', received)
                            self.assertIn('Your commentary and messages go to the manager.', received)
                            self.assertIn(f'action: <next action in {language}>', received)
                            self.assertIn('Your final uses the required result fields.', received)
                        for received in (direct.stdout, complete):
                            self.assertIn(original, received)
                            self.assertIn('1. [status: in_progress] Read the canonical files.', received)
                            self.assertNotIn('Check the local record shapes.', received)
                        self.assertEqual(evidence.read_bytes(), original.encode('utf-8'))

    def test_invalid_language_publishes_nothing_then_corrected_call_is_usable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            question = root / 'question.txt'
            question.write_text('Read-only question.', encoding='utf-8')
            for index, invalid in enumerate((None, '', ' ', 'German\nEnglish', 'German\rEnglish')):
                with self.subTest(invalid=invalid):
                    assignment = root / f'assignment-{index}.txt'
                    args = ['--project-root', root, '--role', 'explorer', '--supplemental-context', question,
                            '--format', 'create', '--project-name', 'Fixture', '--worker-number', '1',
                            '--model', 'gpt-6-sol', '--thinking', 'high', '--assignment-file', assignment]
                    extra = [] if invalid is None else ['--communication-language', invalid]
                    failed = self.run_builder('build_dispatch_prompt.py', *args, *extra,
                                              auto_file=False, auto_language=False)
                    self.assertNotEqual(failed.returncode, 0)
                    self.assertEqual(failed.stdout, '')
                    self.assertFalse(assignment.exists())
                    self.assertIn('--communication-language', failed.stderr)
                    self.assertIn('usage:', failed.stderr)
                    if invalid is not None:
                        self.assertIn('nonempty single-line', failed.stderr)
                    corrected = self.consume(self.run_builder('build_dispatch_prompt.py', *args,
                        '--communication-language', 'German', auto_file=False, auto_language=False))
                    self.assertIn('Communication language: German.', self.prompt(corrected))

    def test_explorer_question_needs_no_plan_and_rejects_execution_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            facts = root / 'question.txt'
            facts.write_text('Question: Ä 中文 — "Wer besitzt dieses Verhalten?" No external access.', encoding='utf-8')
            base = ['--communication-language', 'German', '--project-root', root, '--role', 'explorer', '--format', 'create', '--project-name', 'Fixture', '--worker-number', '1',
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
                self.assertIn('Communication language: German.', text)
                self.assertIn('Keep required field names, status values, quotes, relay text and technical literals exact.', text)
            self.assertIn(facts.read_text(encoding='utf-8'), prompt)
            self.assertIn('do not implement, change project files, run tests', prompt)
            self.assertIn('No review acceptance', prompt)
            for field in ('status: done | blocked', 'answer:', 'evidence:', 'blocker:', 'limits:'):
                self.assertIn(field, prompt)
            self.assertIn('native final only', prompt)
            self.assertIn('Do not also send a duplicate result.', prompt)
            self.assertIn('SC-EXP-1:', prompt)
            self.assertFalse((root / 'PROJECT_INDEX.md').exists())

    def test_explorer_optional_plan_unit_keeps_identity_and_context(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            facts = Path(directory) / 'question.txt'
            facts.write_text('Question: identify the owner for this Step. Read-only.', encoding='utf-8')
            result = self.run_builder('build_dispatch_prompt.py', '--communication-language', 'German', '--project-root', root,
                '--role', 'explorer', '--unit', 'W-001/step-1', '--format', 'create', '--project-name', 'Fixture', '--worker-number', '1',
                '--model', 'gpt-6-sol', '--thinking', 'high', '--supplemental-context', facts)
            prompt = self.prompt(self.consume(result))
            self.assertIn('## Non-goals', prompt)
            self.assertIn('## Work Item context', prompt)
            self.assertIn('SC-EXP-1: Fixture · PLAN-0001/W-001/step-1', prompt)

    def test_role_input_failures_then_literal_safe_complete_consumer(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'project Ä 中文'
            copy_started_profile(root)
            facts = base / 'facts.txt'
            facts.write_text('Review only this assigned unit. No commits.', encoding='utf-8')
            for flag, role in [('--executor-result', 'reviewer'), ('--reviewer-result', 'executor'),
                               ('--supplemental-context', 'explorer')]:
                with self.subTest(flag=flag):
                    source = base / (flag[2:] + ' Ä 中文.txt')
                    assignment = base / (flag[2:] + '-assignment.txt')
                    arguments = ['--communication-language', 'German', '--project-root', root, '--format', 'create', '--project-name', 'Fixture',
                        '--worker-number', '1', '--model', 'gpt-6-sol', '--thinking', 'high',
                        '--unit', 'W-001/step-1', '--role', role, '--assignment-file', assignment, flag, source]
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
        examples = [block.strip() for block in re.findall(r'^[ \t]*```text\n(.*?)\n[ \t]*```[ \t]*$', instructions, re.S | re.M)
                    if 'build_dispatch_prompt.py' in block and '--format create' in block]
        self.assertEqual(len(examples), 1)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project with spaces'
            copy_started_profile(root, step=2)
            config = root / '.scoville/config.json'
            config.parent.mkdir(exist_ok=True)
            config.write_text(json.dumps({'workflow': {'execute': {'low': {'model': 'gpt-6-sol', 'reasoning': 'high'}}}}), encoding='utf-8')
            example = examples[0].replace('PLAN-NNNN', 'PLAN-0001')
            values = {'workflow': PACKAGE.as_posix(), 'absolute-workspace': root.as_posix(),
                      'own-agent-handle': '/root/manager', 'project': 'Änderung 中文',
                      'number': '9', 'class': 'low', 'language': 'German'}
            for key, value in values.items():
                example = example.replace('<' + key + '>', value)
            self.assertNotRegex(example, r'<[^>]+>')
            built = subprocess.run([sys.executable, *shlex.split(example)[1:]], capture_output=True, text=True, encoding='utf-8')
            payload = self.consume(built)
            match = re.search(r'assignment from (.*?) before any project work', payload['message'])
            self.assertIsNotNone(match)
            assignment = Path(match[1]); self.addCleanup(assignment.unlink, missing_ok=True)
            self.assertFalse(assignment.is_relative_to(root))
            self.assertIn('2. [status: in_progress] Check the local record shapes.', assignment.read_text(encoding='utf-8'))
            self.assertLess(len(built.stdout.encode('utf-8')), 4096)

    def run_builder(self, script, *arguments, auto_file=True, auto_language=True):
        if auto_language and script == 'build_dispatch_prompt.py' and '--communication-language' not in arguments:
            arguments = (*arguments, '--communication-language', 'German')
        # These contract fixtures explicitly choose their role pair. Production
        # default routing and unjustified overrides are tested separately.
        if '--model' in arguments and '--thinking' in arguments:
            arguments = (*arguments, '--override-reason', 'Fixture explicit role choice')
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
            self.assertRegex(task_name, r'^scoville_(executor|reviewer|explorer)_[1-9][0-9]*$')
            self.assertEqual(fork_turns, 'none')
            self.assertEqual(model, 'gpt-6-sol')
            self.assertEqual(reasoning_effort, 'high')
            self.assertNotIn('manager_agent_id', message)
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
            copy_started_profile(root)
            commands = [
                ('build_dispatch_prompt.py', ['--communication-language', 'German', '--project-root', root, '--format', 'create',
                 '--project-name', 'Fixture', '--worker-number', '1',
                 '--model', 'gpt-6-sol', '--thinking', 'high', '--override-reason', 'Fixture explicit role choice',
                 '--unit', 'W-001/step-1', '--role', 'executor'])]
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
            copy_started_profile(root)
            evidence = root / 'result.txt'
            evidence.write_text('completed: checked change; remaining work unchanged', encoding='utf-8')
            facts = root / 'review-facts.txt'
            facts.write_text('Initial review of the first Step against its Acceptance. No earlier assessments.', encoding='utf-8')
            common = ['--communication-language', 'German', '--project-root', root, '--format', 'create', '--project-name', 'Änderung 中文', '--worker-number', '7', '--model', 'gpt-6-sol', '--thinking', 'high']
            denied = self.run_builder('build_dispatch_prompt.py', *common, '--unit', 'W-001', '--role', 'executor')
            self.assertNotEqual(denied.returncode, 0)
            self.assertFalse(denied.auto_assignment.exists())
            whole = self.consume(self.run_builder('build_dispatch_prompt.py', *common, '--unit', 'W-001', '--role', 'reviewer', '--executor-result', evidence))
            self.assertIn('Assignment: SC-REV-7: Änderung 中文 · PLAN-0001/W-001', whole['message'])
            for role, extra, label in [('executor', [], 'SC-WRK'), ('reviewer', ['--executor-result', evidence, '--reviewer-result', facts], 'SC-REV'),
                                       ('executor', ['--reviewer-result', evidence], 'SC-WRK')]:
                result = self.consume(self.run_builder('build_dispatch_prompt.py', *common, '--unit', 'W-001/step-1', '--role', role, *extra))
                for text in (result['message'], self.prompt(result)):
                    self.assertIn('Communication language: German.', text)
                    self.assertIn('Keep required field names, status values, quotes, relay text and technical literals exact.', text)
                self.assertIn(f'Assignment: {label}-7: Änderung 中文 · PLAN-0001/W-001/step-1', self.prompt(result))
                self.assertEqual(result['task_name'], f'scoville_{role}_7')
                for obsolete in ('rollover_pending', 'context_handoff', 'check_context_checkpoint', 'TAKEOVER_COMPLETE', 'progress_pending', 'broader assignment'):
                    self.assertNotIn(obsolete, self.prompt(result))
                if role == 'executor':
                    self.assertIn('Return done when this ONE Step and its required checks finish', self.prompt(result))
                self.assertIn(f'suite_directory: {PACKAGE.parent.resolve()}', self.prompt(result))
                self.assertIn('On user stop, stop dependent work', self.prompt(result))
                self.assertNotIn('On context_handoff, state finished Steps', self.prompt(result))
            invalid = self.run_builder('build_dispatch_prompt.py', *common, '--unit', 'W-001/step-1', '--role', 'reviewer')
            self.assertNotEqual(invalid.returncode, 0)
            self.assertEqual(invalid.stdout, '')
            self.assertIn('usage:', invalid.stderr)
            self.assertIn('--executor-result', invalid.stderr)

    def test_repeated_reviews_of_one_worker_spawn_with_distinct_names(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            evidence = root / 'result.txt'
            evidence.write_text('completed: assigned first Step checked; second Step unreleased', encoding='utf-8')
            facts = root / 'review-facts.txt'
            facts.write_text('Initial review of the checked first Step against its Acceptance. No earlier assessments.', encoding='utf-8')
            arguments = ['--communication-language', 'German', '--project-root', root, '--format', 'create', '--project-name', 'fixture', '--worker-number', '2', '--model', 'gpt-6-sol',
                         '--thinking', 'high', '--unit', 'W-001/step-1', '--role', 'reviewer',
                         '--executor-result', evidence, '--reviewer-result', facts]
            assigned = set()
            payloads = []
            for number in (2, 3):
                selected = arguments.copy()
                selected[selected.index('--worker-number') + 1] = str(number)
                payload = self.consume(self.run_builder('build_dispatch_prompt.py', *selected))
                self.assertNotIn(payload['task_name'], assigned, 'Native task name already assigned')
                assigned.add(payload['task_name'])
                payloads.append(payload)
            self.assertEqual({k: v for k, v in payloads[0].items() if k not in ('task_name', 'message')},
                             {k: v for k, v in payloads[1].items() if k not in ('task_name', 'message')})
            self.assertEqual(self.prompt(payloads[0]).replace('SC-REV-2:', 'SC-REV-3:'), self.prompt(payloads[1]))


    def test_wrapped_release_dispatch_does_not_require_an_unselected_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            project = base / 'project'
            copy_started_profile(project)
            for name in ('scoville-code', 'scoville-workflow-for-codex'):
                member = next(m for m in _config['members'] if m['name'] == name)
                for relative, content in _builder.payload(SUITE_ROOT, member, _config).items():
                    target = base / 'packages' / name / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(content)
            script = base / 'packages/scoville-workflow-for-codex/scoville-workflow-for-codex/scripts/build_dispatch_prompt.py'
            code = base / 'packages/scoville-code/scoville-code/SKILL.md'
            assignment = project / 'assignment.txt'
            command = [sys.executable, '-B', str(script), '--communication-language', 'German', '--project-root', str(project), '--unit', 'W-001/step-1',
                       '--role', 'executor', '--format', 'create', '--project-name', 'fixture', '--worker-number', '7', '--model', 'gpt-6-sol', '--thinking', 'high',
                       '--override-reason', 'Fixture explicit role choice',
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
            # Reading files needs no checker; dispatch still needs it for result delivery.
            checker = script.with_name('check_text_size.py')
            checker.unlink()
            assignment = project / 'assignment-without-checker.txt'
            command[-1] = str(assignment)
            missing_checker = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            self.assertNotEqual(missing_checker.returncode, 0)
            self.assertEqual(missing_checker.stdout, '')
            self.assertFalse(assignment.exists())
            self.assertEqual(code.read_bytes(), content)

    def test_old_group_and_free_rewrite_fail_before_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            facts = root / 'facts.txt'; facts.write_text('Rewritten task.', encoding='utf-8')
            common = ['--communication-language', 'German', '--project-root', root, '--format', 'create', '--project-name', 'Fixture', '--model', 'gpt-6-sol', '--thinking', 'high', '--worker-number', '7', '--role', 'executor']
            for extra in (['--unit', 'W-001/steps-1-2'], ['--unit', 'W-001'],
                          ['--unit', 'W-001/step-1', '--supplemental-context', facts]):
                failed = self.run_builder('build_dispatch_prompt.py', *common, *extra)
                self.assertNotEqual(failed.returncode, 0)
                self.assertEqual(failed.stdout, '')
                self.assertFalse(failed.auto_assignment.exists())

    def test_file_assignment_preserves_full_text_and_native_parameters(self):
        # The actual file consumer reads the full published assignment. Native
        # agent interpretation is separate live evidence.
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            facts = root / 'facts.txt'
            body = 'Keep no third-party dependencies. Quotes: "A" and \'B\'.\nScope: Änderung 中文 → exact\\path.\n'
            facts.write_text(body, encoding='utf-8')
            result = root / 'result.txt'
            result.write_text('completed: checked result, unchanged scope.', encoding='utf-8')
            common = ['--communication-language', 'German', '--project-root', root, '--format', 'create', '--project-name', 'Änderung 中文', '--worker-number', '9', '--model', 'gpt-6-sol',
                      '--thinking', 'high', '--unit', 'W-001/step-1', '--reviewer-result', facts]
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
                    self.assertIn('Reading this external assignment file is permitted.', short['message'])
                    self.assertNotIn('--part', short['message'])
                    self.assertNotIn('check_text_size.py', short['message'])
                    self.assertNotIn(body, short['message'])
                    self.assertEqual({k: v for k, v in full.items() if k not in ('message', 'task_name')},
                                     {k: v for k, v in short.items() if k not in ('message', 'task_name')})
                    self.assertEqual(full['task_name'], short['task_name'])
                    self.assertIn(f'scoville_role={role}', assignment.read_text(encoding='utf-8').splitlines())
                    for generated in (full, short):
                        self.assertEqual(generated['task_name'], f'scoville_{role}_9')

    def test_file_assignment_rejects_overwrite_and_invalid_mode_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            common = ['--communication-language', 'German', '--project-root', root, '--format', 'create', '--project-name', 'Fixture', '--worker-number', '9', '--model', 'gpt-6-sol',
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
                        invocation = ['--communication-language', 'German', '--project-root', root, '--unit', 'W-001/step-1', '--role', 'executor']
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
            copy_started_profile(root)
            common = ['--communication-language', 'German', '--project-root', root, '--format', 'create', '--project-name', 'Fixture', '--worker-number', '9', '--thinking', 'high',
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
        result = self.run_builder('build_dispatch_prompt.py', '--communication-language', 'German', '--project-root', PACKAGE,
                                  '--role', 'executor', '--unit', 'W-001', '--format', 'create', )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        for parameter in ('--worker-number', '--project-name', '--model', '--thinking'):
            self.assertIn(parameter, result.stderr)
        self.assertIn('usage:', result.stderr)







    def test_missing_writing_rules_fail_then_corrected_helpers_feed_consumers(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'project'
            copy_started_profile(root)
            copy = base / 'suite' / PACKAGE.name
            shutil.copytree(PACKAGE, copy)
            shutil.copytree(PACKAGE.parent / 'scoville-code', copy.parent / 'scoville-code')
            shutil.copytree(PACKAGE.parent / 'scoville-plan', copy.parent / 'scoville-plan')
            writing = copy / 'references/writing.md'
            original = writing.read_bytes()
            calls = [
                ('build_dispatch_prompt.py', ['--communication-language', 'German', '--project-root', root, '--format', 'create',
                 '--project-name', 'Fixture',
                 '--worker-number', '1', '--model', 'gpt-6-sol', '--thinking', 'high',
                 '--override-reason', 'Fixture explicit role choice',
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

    def test_fresh_dispatch_embeds_required_shell_rules_once_and_keeps_absolute_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / 'project'
            copy_started_profile(root)
            copy = base / 'suite' / PACKAGE.name
            shutil.copytree(PACKAGE, copy)
            shutil.copytree(PACKAGE.parent / 'scoville-code', copy.parent / 'scoville-code')
            shutil.copytree(PACKAGE.parent / 'scoville-plan', copy.parent / 'scoville-plan')
            shell = copy / 'references/shell-commands.md'
            original = shell.read_bytes()
            shell.unlink()
            assignment = root / 'assignment.txt'
            command = [sys.executable, str(copy / 'scripts/build_dispatch_prompt.py'),
                       '--communication-language', 'German', '--project-root', str(root), '--format', 'create',
                       '--project-name', 'Fixture',
                       '--worker-number', '1', '--model', 'gpt-6-sol', '--thinking', 'high',
                       '--override-reason', 'Fixture explicit role choice',
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
            self.assertIn(f'shell_command_rules: {shell.resolve()};', prompt)
            self.assertEqual(prompt.count(shell.read_text(encoding='utf-8')), 1)








if __name__ == '__main__':
    unittest.main()
