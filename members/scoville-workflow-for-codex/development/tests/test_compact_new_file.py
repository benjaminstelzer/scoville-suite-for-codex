"""Keep the compact new-file route within the existing attribution boundary."""
from pathlib import Path
import tempfile
import unittest

from test_contract import PACKAGE, SELECTOR, copy_started_profile, prompt_builder


class CompactNewFileTests(unittest.TestCase):
    def test_same_step_and_complete_report_survive_new_file_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            context = prompt_builder.select_unit(SELECTOR, root, 'W-001/step-1')
            report = 'status: done\nchanges: created.py adds the requested helper; dist/ holds generated copies\nchecks: generator exited 0; expected outputs created in this run\nproblems: none\nlimits: none\n'
            new_file = 'NEW_FILE_CONTENT_READ_SEPARATELY = True\n'
            (root / 'created.py').write_text(new_file, encoding='utf-8')
            before = {p: p.read_bytes() for p in root.rglob('*') if p.is_file()}
            execution = prompt_builder.build_prompt('executor', root, context, {}, 'German')
            review = prompt_builder.build_prompt('reviewer', root, context, {'executor_result': report}, 'German')
            self.assertIn('## executor_result\n' + report, review)
            self.assertIn('1. [status: in_progress] Read the canonical files.', review)
            self.assertNotIn('Check the local record shapes.', review)
            self.assertNotIn(new_file, execution)
            self.assertNotIn(new_file, review)
            self.assertEqual(before, {p: p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_only_fresh_roles_load_standing_rules_but_task_evidence_survives_reuse(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            copy_started_profile(root)
            report = 'status: done\nchanges: none\nchecks: observed\nlimits: none\n'
            for role, unit, inputs in (
                ('executor', 'W-001/step-1', {}),
                ('reviewer', 'W-001/step-1', {'executor_result': report}),
                ('reviewer', 'W-001', {'executor_result': report}),
                ('explorer', None, {'supplemental_context': 'Inspect only the requested owner.'}),
            ):
                context = prompt_builder.select_unit(SELECTOR, root, unit) if unit else {}
                fresh = prompt_builder.build_prompt(role, root, context, inputs, 'German')
                followup = prompt_builder.build_prompt(role, root, context, inputs, 'German', reuse=True)
                for filename in ('writing.md', 'shell-commands.md'):
                    rules = (PACKAGE / 'references' / filename).read_text(encoding='utf-8')
                    self.assertEqual(fresh.count(rules), 1)
                    self.assertNotIn(rules, followup)
                self.assertNotIn('Read applicable AGENTS.md', fresh)
                self.assertNotIn('AGENTS.md', followup)
                self.assertNotIn('Use these fields', followup)
                self.assertNotIn('Choose appropriate Skills', followup)
                for binding in prompt_builder.binding_context(context, reuse=True):
                    self.assertIn(binding, followup)
                for key, value in inputs.items():
                    self.assertIn('## ' + key + '\n' + value, followup)
                self.assertIn('Communication language: German.', followup)
                if role == 'reviewer':
                    self.assertIn('Step review: stay read-only', fresh)
                    self.assertIn('Closure review: stay read-only', fresh)
                    self.assertIn('Task: ' + ('Step review' if '/' in unit else 'Closure review'), followup)
                    self.assertNotIn('stay read-only', followup)


if __name__ == '__main__':
    unittest.main()
