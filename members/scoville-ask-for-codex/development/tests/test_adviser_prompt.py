from pathlib import Path
import os
import json
import importlib.util
import subprocess
import sys
import tempfile
import unittest


SUITE = Path(__file__).resolve().parents[4]
_spec = importlib.util.spec_from_file_location('ask_prompt_test_build', SUITE / 'development/build_suite.py')
_builder = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_builder)
_package_temp = tempfile.TemporaryDirectory(prefix='ask-prompt-tests-', ignore_cleanup_errors=True)
_config = _builder.load(SUITE, 'codex')
_member = next(m for m in _config['members'] if m['name'] == 'scoville-ask-for-codex')
for _name, _content in _builder.payload(SUITE, _member, _config).items():
    _target = Path(_package_temp.name) / _name
    _target.parent.mkdir(parents=True, exist_ok=True)
    _target.write_bytes(_content)
PACKAGE = Path(_package_temp.name) / 'scoville-ask-for-codex'
SCRIPT = PACKAGE / "scripts/build_adviser_prompt.py"


class AdviserPromptTests(unittest.TestCase):
    SPAWN = ['--format', 'spawn', '--task-name', 'ask_custom_sol_1',
             '--model', 'gpt-6-sol', '--effort', 'high']

    def run_prompt(self, question="Prüfe café ✓ ohne Änderungen.", extra=()):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "question.txt"
            source.write_text(question, encoding="utf-8")
            env = dict(os.environ)
            # Agent dispatch must not depend on a valid calling chat identity.
            env["CODEX_THREAD_ID"] = "not-a-chat-uuid"
            return subprocess.run(
                [sys.executable, str(SCRIPT), "--question-file", str(source),
                 "--workspace-root", directory, "--adviser-id", "custom-sol",
                 "--mode", "review", "--scope", "Patch ä", "--reference", "review-1", *extra],
                env=env, capture_output=True, text=True, encoding="utf-8", check=False,
            )

    def test_spawn_arguments_preserve_settings_identity_and_read_only_contract(self):
        result = self.run_prompt(extra=self.SPAWN)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(set(data), {'task_name', 'message', 'fork_turns', 'model', 'reasoning_effort'})
        self.assertEqual(data['task_name'], 'ask_custom_sol_1')
        self.assertEqual(data['fork_turns'], 'none')
        self.assertEqual(data['model'], 'gpt-6-sol')
        self.assertEqual(data['reasoning_effort'], 'high')
        self.assertIn('adviser_id: custom-sol', data['message'])
        self.assertIn('consultation_reference: review-1', data['message'])
        self.assertIn('scope: Patch ä', data['message'])
        self.assertIn('Prüfe café ✓', data['message'])
        self.assertIn('Do not create, edit, move or delete', data['message'])
        self.assertIn('collaboration.send_message', data['message'])
        self.assertIn('complete answer as your final agent response', data['message'])
        self.assertNotIn('calling_thread_id:', data['message'])
        self.assertNotIn('not-a-chat-uuid', data['message'])

    def test_missing_spawn_fields_name_argument_and_corrected_call_succeeds(self):
        for flag in ('--task-name', '--model', '--effort'):
            args = self.SPAWN.copy()
            index = args.index(flag)
            del args[index:index + 2]
            with self.subTest(flag=flag):
                invalid = self.run_prompt(extra=args)
                self.assertNotEqual(invalid.returncode, 0)
                self.assertEqual(invalid.stdout, '')
                self.assertIn(flag, invalid.stderr)
                self.assertIn('usage:', invalid.stderr)
                corrected = self.run_prompt(extra=self.SPAWN)
                self.assertEqual(corrected.returncode, 0, corrected.stderr)
                self.assertEqual(json.loads(corrected.stdout)['fork_turns'], 'none')

    def test_prompt_preserves_complete_request_and_each_packaged_rule_once(self):
        request = "Prüfe café ✓ ohne Änderungen.\nErhalt: [x] und `code`."
        result = self.run_prompt(request)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(request, result.stdout)
        self.assertIn('workspace_root:', result.stdout)
        for name in ('adviser.md', 'native-delivery.md'):
            rules = (PACKAGE / 'references' / name).read_text(encoding='utf-8')
            self.assertEqual(result.stdout.count(rules), 1)

    def test_resolved_selected_advisers_feed_prompt_builder_without_repair(self):
        with tempfile.TemporaryDirectory() as project:
            resolved = subprocess.run([sys.executable, str(PACKAGE / 'scripts/ask.py'),
                '--project-root', project, '--adviser', 'sol', '--adviser', 'astra'],
                capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(resolved.returncode, 0, resolved.stderr)
        advisers = json.loads(resolved.stdout)['config']['advisers']
        self.assertEqual([a['id'] for a in advisers], ['sol', 'astra'])
        for adviser in advisers:
            with self.subTest(adviser=adviser['id']):
                result = self.run_prompt(extra=['--format', 'spawn', '--task-name', 'ask_' + adviser['id'],
                    '--adviser-id', adviser['id'], '--model', adviser['model'], '--effort', adviser['effort']])
                self.assertEqual(result.returncode, 0, result.stderr)
                arguments = json.loads(result.stdout)
                self.assertEqual(arguments['model'], adviser['model'])
                self.assertEqual(arguments['reasoning_effort'], adviser['effort'])
                self.assertIn('adviser_id: ' + adviser['id'], arguments['message'])
                self.assertEqual(arguments['fork_turns'], 'none')

    def test_host_owns_model_availability_without_helper_substitution(self):
        result = self.run_prompt(extra=self.SPAWN + ['--model', 'unavailable-host-model'])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)['model'], 'unavailable-host-model')

    def test_invalid_input_never_emits_partial_assignment_and_corrected_call_works(self):
        for kwargs, diagnostic in (
            ({'question': '  '}, 'must contain the request'),
            ({'extra': ['--scope', 'a\nb']}, 'single-line'),
            ({'extra': ['--reference', '']}, 'single-line'),
            ({'extra': ['--adviser-id', 'Custom-Sol']}, 'lowercase adviser ID'),
            ({'extra': ['--workspace-root', 'relative-project']}, 'existing absolute directory'),
            ({'extra': ['--mode', 'execute']}, 'invalid choice'),
            ({'extra': self.SPAWN + ['--task-name', 'ask-wrong']}, '--task-name'),
            ({'extra': self.SPAWN + ['--model', 'two words']}, '--model'),
            ({'extra': self.SPAWN + ['--effort', 'unsupported']}, 'invalid choice'),
            ({'extra': ['--model', 'gpt-6-sol']}, 'require --format spawn'),
        ):
            with self.subTest(kwargs=kwargs):
                result = self.run_prompt(**kwargs)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, '')
                self.assertIn(diagnostic, result.stderr)
                self.assertIn('usage:', result.stderr)
                corrected = self.run_prompt(extra=self.SPAWN)
                self.assertEqual(corrected.returncode, 0, corrected.stderr)
                self.assertEqual(json.loads(corrected.stdout)['task_name'], 'ask_custom_sol_1')

    def test_missing_question_is_diagnostic_then_corrected(self):
        result = self.run_prompt(extra=['--question-file', 'nonexistent-w002-question.txt'])
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, '')
        self.assertIn('cannot read required UTF-8 input', result.stderr)
        corrected = self.run_prompt()
        self.assertEqual(corrected.returncode, 0, corrected.stderr)


if __name__ == '__main__':
    unittest.main()
