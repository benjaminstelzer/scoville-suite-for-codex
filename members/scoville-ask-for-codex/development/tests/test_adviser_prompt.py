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
CALLER = "01a0e778-0c80-7660-b8b9-c8ce59a9fed4"
OTHER = "01a0ebd5-922f-7ff0-88ba-bfe0699c8313"


class AdviserPromptTests(unittest.TestCase):
    def test_creation_arguments_and_corrected_missing_parameter(self):
        extra = ['--format', 'create', '--project-id', 'saved-project',
                 '--adviser-id', 'astra', '--caller-title', 'Review patch', '--model', 'gpt-6-astra']
        invalid = self.run_prompt(extra=extra)
        self.assertNotEqual(invalid.returncode, 0)
        self.assertEqual(invalid.stdout, '')
        self.assertIn('--thinking', invalid.stderr)
        self.assertIn('usage:', invalid.stderr)
        result = self.run_prompt(extra=extra + ['--thinking', 'medium'])
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data['title'], 'SC-ASK-ASTRA: Review patch')
        self.assertEqual(data['model'], 'gpt-6-astra')
        self.assertEqual(data['target'], {'type': 'project', 'projectId': 'saved-project', 'environment': {'type': 'local'}})
        self.assertIn('Prüfe café ✓', data['prompt'])
        wrong_mode = self.run_prompt(extra=['--model', 'gpt-6-astra'])
        self.assertNotEqual(wrong_mode.returncode, 0)
        self.assertEqual(wrong_mode.stdout, '')
        self.assertIn('use --format create', wrong_mode.stderr)

    def test_short_label_uses_resolved_adviser_not_a_model_guess(self):
        args = ['--format', 'create', '--project-id', 'saved-project', '--caller-title', 'Prüfe den Patch',
                '--model', 'gpt-6-sol', '--thinking', 'high']
        missing = self.run_prompt(extra=args)
        self.assertNotEqual(missing.returncode, 0)
        self.assertEqual(missing.stdout, '')
        self.assertIn('--adviser-id', missing.stderr)
        self.assertIn('usage:', missing.stderr)
        corrected = self.run_prompt(extra=args + ['--adviser-id', 'Custom-Sol'])
        self.assertEqual(corrected.returncode, 0, corrected.stderr)
        data = json.loads(corrected.stdout)
        self.assertEqual(data['title'], 'SC-ASK-CUSTOM-SOL: Prüfe den Patch')
        self.assertEqual(data['model'], 'gpt-6-sol')

    def run_prompt(self, question="Prüfe café ✓ ohne Änderungen.", extra=(), caller=CALLER):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "question.txt"
            source.write_text(question, encoding="utf-8")
            env = dict(os.environ)
            env.pop("CODEX_THREAD_ID", None)
            if caller is not None:
                env["CODEX_THREAD_ID"] = caller
            return subprocess.run(
                [sys.executable, str(SCRIPT), "--question-file", str(source),
                 "--mode", "review", "--scope", "Patch ä", "--reference", "review-1", *extra],
                env=env, capture_output=True, text=True, encoding="utf-8", check=False,
            )

    def test_complete_prompt_preserves_request_rules_and_recipient(self):
        request = "Prüfe café ✓ ohne Änderungen.\nErhalt: [x] und `code`."
        result = self.run_prompt(request)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(request, result.stdout)
        self.assertIn(f"calling_thread_id: {CALLER}", result.stdout)
        self.assertIn("scope: Patch ä", result.stdout)
        for name in ("adviser.md", "native-delivery.md"):
            rules = (PACKAGE / "references" / name).read_text(encoding="utf-8")
            self.assertEqual(result.stdout.count(rules), 1)
        self.assertNotIn("creation_authorized:", result.stdout)

    def test_optional_caller_provenance_and_override(self):
        result = self.run_prompt(extra=("--caller-thread-id", OTHER))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f"calling_thread_id: {OTHER}", result.stdout)
        self.assertNotIn(CALLER, result.stdout)
        without = self.run_prompt(caller=None)
        self.assertEqual(without.returncode, 0, without.stderr)
        self.assertNotIn('calling_thread_id:', without.stdout)
        self.assertIn('final response in this adviser chat', without.stdout)
        self.assertNotIn('RESULT NOT DELIVERED', without.stdout)

    def test_invalid_input_never_emits_a_partial_assignment(self):
        for kwargs, diagnostic in (
            ({"caller": "review title"}, "calling chat's UUID"),
            ({"question": "  "}, "must contain the request"),
            ({"extra": ("--scope", "a\nb")}, "single-line"),
            ({"extra": ("--reference", "")}, "single-line"),
            ({"extra": ("--mode", "execute")}, "invalid choice"),
        ):
            with self.subTest(kwargs=kwargs):
                result = self.run_prompt(**kwargs)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")
                self.assertIn(diagnostic, result.stderr)

    def test_missing_question_is_diagnostic(self):
        result = self.run_prompt(extra=("--question-file", "nonexistent-plan0020-question.txt"))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("cannot read required UTF-8 input", result.stderr)


if __name__ == "__main__":
    unittest.main()
