"""Real selector-to-child projection, with exact Step text and closure coverage."""
import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_contract import PACKAGE, SUITE_ROOT, prompt_builder


class SelectedContextTests(unittest.TestCase):
    def prepare(self, directory, ending):
        root = Path(directory) / 'project'
        shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
        path = root / 'docs/plans/0001-validate-profile.md'
        text = path.read_text(encoding='utf-8').replace(
            '1. Read the canonical files.\n2. Check the local record shapes.',
            '1. [status: done] OUTSIDE-FIRST.\n'
            '2. [status: in_progress] [execute: reasoning=high] Preserve café and `中文`.\n'
            '3. SELECTED-THIRD: verify ✓ unchanged.  \n'
            '4. OUTSIDE-LAST.').replace('Steps:\n', 'Instructions: Preserve exact literals.\nSteps:\n', 1)
        text = text.replace('Evidence: []', 'Evidence: HISTORY-ONLY', 1)
        path.write_bytes(text.replace('\n', ending).encode('utf-8'))
        return root

    def test_single_range_whole_and_no_unit_across_roles(self):
        for ending in ('\n', '\r\n'):
            with self.subTest(ending=repr(ending)), tempfile.TemporaryDirectory() as directory:
                root = self.prepare(directory, ending)
                before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
                for unit in ('W-001/step-2', 'W-001/steps-2-3', 'W-001'):
                    context = prompt_builder.select_unit(PACKAGE / 'scripts/select_context.py', root, unit)
                    item = context['work_item']
                    contexts = []
                    for role, role_input in (
                        ('executor', {}),
                        ('executor', {'reviewer_result': 'changes_requested: correct this unit only.'}),
                        ('executor', {'supplemental_context': 'Retained effects checked. Only this unit remains.'}),
                        ('reviewer', {'executor_result': 'completed: owner.py changed; focused check passed.',
                                      'supplemental_context': 'DELTA: owner.py against pre-work. Reuse unchanged earlier coverage.'}),
                        ('explorer', {'supplemental_context': 'Investigate the selected scope only.'}),
                    ):
                        with self.subTest(unit=unit, role=role, inputs=role_input):
                            prompt = prompt_builder.build_prompt(role, root, '/root/manager', '', context, role_input)
                            embedded = prompt.split('## Work Item context\n', 1)[1].split('\n## ', 1)[0]
                            contexts.append(embedded)
                            for key in ('header', 'status', 'depends_on', 'blocked_by', 'decisions', 'outcome', 'acceptance'):
                                self.assertIn(item[key], embedded)
                            self.assertIn('Instructions: Preserve exact literals.', embedded)
                            self.assertIn('Steps:\n' + item['source_text'] if '/' in unit else item['context_text'].rstrip(), embedded)
                            self.assertEqual(prompt.count(item['source_text'].rstrip('\n')), 1)
                            for value in role_input.values():
                                self.assertIn(value, prompt)
                            if '/' in unit:
                                for excluded in ('OUTSIDE-FIRST', 'OUTSIDE-LAST', 'Evidence:', 'HISTORY-ONLY', 'Next action:'):
                                    self.assertNotIn(excluded, embedded)
                                self.assertNotIn('Step 1: done', prompt)
                                self.assertNotIn('Step 4: unknown', prompt)
                                if unit.endswith('step-2'):
                                    self.assertNotIn('SELECTED-THIRD', embedded)
                                else:
                                    self.assertLess(embedded.index('2. [status:'), embedded.index('3. SELECTED-THIRD'))
                            else:
                                self.assertIn('OUTSIDE-FIRST', embedded)
                                self.assertIn('OUTSIDE-LAST', embedded)
                    self.assertTrue(all(value.rstrip('\n') == contexts[0].rstrip('\n') for value in contexts))
                no_unit = prompt_builder.build_prompt('explorer', root, '/root/manager', '', {},
                    {'supplemental_context': 'Question without Plan context.'})
                self.assertNotIn('## Work Item context', no_unit)
                self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_selected_context_fails_closed_without_complete_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.prepare(directory, '\n')
            context = prompt_builder.select_unit(PACKAGE / 'scripts/select_context.py', root, 'W-001/steps-2-3')
            # Complete internal context is unnecessary for selected units.
            del context['work_item']['context_text']
            self.assertIn('3. SELECTED-THIRD', prompt_builder.work_item_context(context['work_item']))
            for field in ('unit', 'source_text', 'header', 'status', 'depends_on', 'blocked_by', 'decisions', 'outcome', 'acceptance', 'instructions'):
                broken = copy.deepcopy(context)
                broken['work_item'][field] = None
                for role, inputs in (('executor', {}), ('explorer', {'supplemental_context': 'Question.'})):
                    with self.subTest(field=field, role=role), self.assertRaisesRegex(ValueError, 'SELECTOR_INCOMPATIBLE'):
                        prompt_builder.build_prompt(role, root, '/root/manager', '', broken, inputs)

    def test_whole_item_closure_keeps_all_steps_and_scoped_delta(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.prepare(directory, '\n')
            facts = Path(directory) / 'review.txt'
            facts.write_text('DELTA: owner.py only against pre-work. Reuse unchanged prior coverage. '
                             'Also check every Step and full Acceptance for Work Item closure.', encoding='utf-8')
            result = Path(directory) / 'result.txt'
            result.write_text('completed: owner.py changed; focused check passed.', encoding='utf-8')
            assignment = Path(directory) / 'assignment.txt'
            run = subprocess.run([sys.executable, str(PACKAGE / 'scripts/build_dispatch_prompt.py'),
                '--project-root', str(root), '--unit', 'W-001', '--role', 'reviewer',
                '--manager-agent-id', '/root/manager', '--format', 'create', '--route', 'medium',
                '--project-name', 'Fixture', '--worker-number', '1', '--assignment-file', str(assignment),
                '--executor-result', str(result), '--supplemental-context', str(facts)],
                capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn('PLAN-0001/W-001/steps-1-4', json.loads(run.stdout)['message'])
            prompt = assignment.read_text(encoding='utf-8')
            complete = prompt_builder.select_unit(PACKAGE / 'scripts/select_context.py', root, 'W-001')['work_item']['context_text'].rstrip()
            self.assertEqual(prompt.count(complete), 1)
            self.assertIn(facts.read_text(encoding='utf-8'), prompt)
            self.assertIn('Do not widen the review', prompt.replace('do not widen the review', 'Do not widen the review'))
            self.assertIn('No tests or project-file changes.', json.loads(run.stdout)['message'])


if __name__ == '__main__':
    unittest.main()
