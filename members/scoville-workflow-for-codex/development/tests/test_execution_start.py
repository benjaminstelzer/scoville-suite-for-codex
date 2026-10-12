"""Execution publication requires the actual saved profile and started unit."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from test_contract import PACKAGE, copy_started_profile
import test_native_creation as native_tests


class ExecutionStartTests(unittest.TestCase):
    run_builder = native_tests.NativeCreationTests.run_builder
    consume = native_tests.NativeCreationTests.consume
    prompt = native_tests.NativeCreationTests.prompt

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / 'project'
        copy_started_profile(self.root)
        self.plan = self.root / 'docs/plans/0001-validate-profile.md'
        self.original = self.plan.read_text(encoding='utf-8')
        self.assignment = self.base / 'assignment.txt'

    def build(self, *extra, role='executor', script=None):
        return self.run_builder(script or 'build_dispatch_prompt.py',
            '--communication-language', 'German',
            '--project-root', self.root, '--plan', 'PLAN-0001', '--unit', 'W-001/step-1',
            '--role', role, '--format', 'create', '--project-name', 'fixture',
            '--worker-number', '1', '--model', 'gpt-6-sol', '--thinking', 'high',
            '--assignment-file', self.assignment, *extra, auto_file=False)

    def rejected(self, run):
        self.assertNotEqual(run.returncode, 0)
        self.assertEqual(run.stdout, '')
        self.assertFalse(self.assignment.exists())

    def test_invalid_graph_blocks_publication_and_corrected_same_call_succeeds(self):
        self.plan.write_text(self.original.replace('Depends on: [W-001]', 'Depends on: [W-999]'), encoding='utf-8')
        run = self.build()
        self.rejected(run)
        self.assertIn('W-999', run.stderr)
        self.assertIn('validation', run.stderr.lower())
        self.plan.write_text(self.original, encoding='utf-8')
        result = self.consume(self.build())
        self.assertIn('1. [status: in_progress] Read the canonical files.', self.prompt(result))

    def test_unstarted_or_paused_unit_blocks_even_when_profile_is_valid(self):
        for status in ('todo', 'done'):
            with self.subTest(status=status):
                self.plan.write_text(self.original.replace('1. [status: in_progress]', f'1. [status: {status}]'), encoding='utf-8')
                run = self.build()
                self.rejected(run)
                self.assertIn('in_progress', run.stderr)
        self.plan.write_text(self.original.replace('Status: in_progress', 'Status: paused', 1), encoding='utf-8')
        self.rejected(self.build())

    def test_read_only_review_needs_no_execution_start(self):
        self.plan.write_text(self.original.replace('1. [status: in_progress]', '1. [status: done]'), encoding='utf-8')
        evidence = self.base / 'executor.txt'
        evidence.write_text('status: done\nchanges: none\nchecks: source read\n', encoding='utf-8')
        self.consume(self.build('--executor-result', evidence, role='reviewer'))

    def test_correction_preserves_native_objections_and_changes_no_project_file(self):
        review = self.base / 'review.txt'
        original = 'status: blocked\nblocker: Missing exact before lines for owner.py.\n'
        review.write_text(original, encoding='utf-8')
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        native = self.consume(self.build('--reviewer-result', review))
        self.assertIn(original, self.prompt(native))
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()})

    def test_missing_bundled_validator_blocks_then_restored_copy_succeeds(self):
        copy = self.base / PACKAGE.name
        shutil.copytree(PACKAGE, copy)
        validator = copy / 'scripts/validate_profile.py'
        source = validator.read_bytes()
        validator.unlink()
        script = str(copy / 'scripts/build_dispatch_prompt.py')
        self.rejected(self.build(script=script))
        validator.write_bytes(source)
        self.consume(self.build(script=script))


if __name__ == '__main__':
    unittest.main()
