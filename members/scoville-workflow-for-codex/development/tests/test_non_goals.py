"""Literal constraints through packaged dispatch, including corrections and limits."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_contract import PACKAGE, SUITE_ROOT, prompt_builder


class NonGoalsTests(unittest.TestCase):
    def prepare(self, directory, exclusions, newline='\n'):
        root = Path(directory) / 'project'
        shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
        plan = root / 'docs/plans/0001-validate-profile.md'
        text = plan.read_text(encoding='utf-8')
        start, end = text.index('## Non-goals'), text.index('\n\n## Work items')
        text = text[:start] + exclusions + text[end:]
        text = text.replace('## Goal\n', '## Goal\n\nGOAL_SENTINEL', 1)
        plan.write_bytes(text.replace('\n', newline).encode('utf-8'))
        return root

    def call(self, root, role='executor', extra=()):
        return subprocess.run([sys.executable, str(PACKAGE / 'scripts/build_dispatch_prompt.py'),
                               '--project-root', str(root), '--unit', 'W-001', '--role', role,
                               '--manager-agent-id', '/root/manager', *extra], capture_output=True)

    def test_literal_exclusions_all_routes_and_newlines(self):
        exclusions = '## Non-goals\n\n- No publication.\n- Preserve ü, 日本語 and `literal`.  '
        for newline in ('\n', '\r\n'):
            with self.subTest(newline=repr(newline)), tempfile.TemporaryDirectory() as directory:
                root = self.prepare(directory, exclusions, newline)
                literal = exclusions.replace('\n', newline)
                context = prompt_builder.select_unit(PACKAGE / 'scripts/select_context.py', root, 'W-001')
                self.assertEqual(context['plan']['non_goals'], literal)
                result_file = Path(directory) / 'result.txt'
                result_file.write_text('Completed scoped work.', encoding='utf-8')
                supplement = Path(directory) / 'supplement.txt'
                supplement.write_text('Preserve completed effects; only named remaining work is released.', encoding='utf-8')
                routes = [('executor', []), ('reviewer', ['--executor-result', str(result_file), '--supplemental-context', str(supplement)]),
                          ('executor', ['--reviewer-result', str(result_file)])]
                routes.append(('executor', ['--supplemental-context', str(supplement)]))
                routes.append(('explorer', ['--supplemental-context', str(supplement)]))
                for role, extra in routes:
                    with self.subTest(role=role, extra=extra):
                        result = self.call(root, role, extra)
                        self.assertEqual(result.returncode, 0, result.stderr)
                        prompt = result.stdout.decode('utf-8')
                        self.assertIn('\n' + literal, prompt)
                        self.assertEqual(prompt.count('## Non-goals'), 1)
                        self.assertNotIn('## Plan-wide exclusions', prompt)
                        self.assertEqual(prompt.count(literal), 1)
                        self.assertNotIn('GOAL_SENTINEL', prompt)
                        self.assertNotIn('## Decisions', prompt)
                assignment = Path(directory) / 'assignment.txt'
                result = self.call(root, extra=['--format', 'create', '--model', 'gpt-6-sol', '--thinking', 'high',
                                               '--project-name', 'Fixture', '--worker-number', '1',
                                               '--assignment-file', str(assignment)])
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(len(json.loads(result.stdout)), 5)
                self.assertIn(literal.encode('utf-8'), assignment.read_bytes())

    def test_utf8_boundary_overflow_and_corrected_call_publish_nothing_on_error(self):
        prefix = '## Non-goals\n\n- '
        exclusions = prefix + 'ü' * 100 + 'x' * (8192 - len(prefix.encode('utf-8')) - 200)
        self.assertEqual(len(exclusions.encode('utf-8')), 8192)
        with tempfile.TemporaryDirectory() as directory:
            root = self.prepare(directory, exclusions + 'x')
            assignment = Path(directory) / 'assignment.txt'
            extra = ['--format', 'create', '--model', 'gpt-6-sol', '--thinking', 'high',
                     '--project-name', 'Fixture', '--worker-number', '1', '--assignment-file', str(assignment)]
            failed = self.call(root, extra=extra)
            self.assertNotEqual(failed.returncode, 0)
            self.assertEqual(failed.stdout, b'')
            self.assertIn(b'NON_GOALS_TOO_LARGE', failed.stderr)
            self.assertIn(b'8193', failed.stderr)
            self.assertFalse(assignment.exists())
            plan = root / 'docs/plans/0001-validate-profile.md'
            text = plan.read_text(encoding='utf-8').replace(exclusions + 'x', exclusions)
            plan.write_text(text, encoding='utf-8', newline='\n')
            corrected = self.call(root, extra=extra)
            self.assertEqual(corrected.returncode, 0, corrected.stderr)
            self.assertIn(exclusions.encode('utf-8'), assignment.read_bytes())

    def test_missing_selector_constraints_are_not_silently_omitted(self):
        context = {'plan': {}, 'work_item': {'unit': 'W-001', 'source_text': 'Work', 'context_text': 'Work'}}
        with self.assertRaisesRegex(ValueError, 'SELECTOR_INCOMPATIBLE'):
            prompt_builder.build_prompt('executor', PACKAGE, '/root/manager', '', context, {})

    def test_explorer_context_rejects_oversized_exclusions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.prepare(directory, '## Non-goals\n\n- ' + 'ü' * 4096)
            facts = Path(directory) / 'question.txt'
            facts.write_text('Question: identify the owner. Read-only.', encoding='utf-8')
            assignment = Path(directory) / 'assignment.txt'
            failed = self.call(root, role='explorer', extra=['--supplemental-context', str(facts),
                '--format', 'create', '--model', 'gpt-6-sol', '--thinking', 'high',
                '--project-name', 'Fixture', '--worker-number', '1', '--assignment-file', str(assignment)])
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn(b'NON_GOALS_TOO_LARGE', failed.stderr)
            self.assertFalse(assignment.exists())


if __name__ == '__main__':
    unittest.main()
