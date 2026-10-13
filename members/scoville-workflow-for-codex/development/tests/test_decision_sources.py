"""Current Decision identity and fail-closed dispatch, without a cache registry."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_contract import SELECTOR, copy_started_profile, prompt_builder

class DecisionSourceTests(unittest.TestCase):
    def setup_project(self, directory):
        root = Path(directory) / 'records'
        copy_started_profile(root)
        decision = next((root / 'docs/decisions').glob('0001-*.md'))
        return root, decision

    def test_fresh_full_reuse_identity_for_every_role_and_exact_utf8_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root, source = self.setup_project(directory)
            text = source.read_text(encoding='utf-8') + '\nDECISION_BODY_café\n'
            source.write_bytes(text.replace('\n', '\r\n').encode('utf-8'))
            context = prompt_builder.select_unit(SELECTOR, root, 'W-001/step-1')
            identity = context['decision_sources'][0]
            self.assertEqual(identity['sha256'], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual(identity['path'], str(source.resolve()))
            for role, inputs in [('executor', {}), ('reviewer', {'executor_result':'status: done\nchanges: none\n'}), ('explorer', {'supplemental_context':'Inspect only.'})]:
                fresh = prompt_builder.build_prompt(role, Path(directory), context, inputs, 'German')
                reuse = prompt_builder.build_prompt(role, Path(directory), context, inputs, 'German', reuse=True)
                self.assertIn(context['decisions'][0], fresh)
                self.assertNotIn('DECISION_BODY_café', reuse)
                for value in identity.values(): self.assertIn(value, reuse)
                self.assertIn(context['plan']['non_goals'], reuse)
                self.assertIn(context['work_item']['source_text'], reuse)
                self.assertNotIn('Check the local record shapes.', reuse)
                for prompt in (fresh, reuse):
                    scope = prompt.index(prompt_builder.PLAN_CONTEXT_SCOPE)
                    self.assertEqual(prompt.count(prompt_builder.PLAN_CONTEXT_SCOPE), 1)
                    self.assertLess(scope, prompt.index('## Plan identity'))
                    self.assertLess(scope, prompt.index(context['plan']['non_goals']))

    def test_new_changed_superseded_and_removed_sources(self):
        with tempfile.TemporaryDirectory() as directory:
            root, source = self.setup_project(directory)
            before = prompt_builder.select_unit(SELECTOR, root, 'W-001/step-1')
            text = source.read_text(encoding='utf-8')
            source.write_text(text + '\nNew stop.\n', encoding='utf-8')
            changed = prompt_builder.select_unit(SELECTOR, root, 'W-001/step-1')
            self.assertNotEqual(before['decision_sources'][0]['sha256'], changed['decision_sources'][0]['sha256'])
            source.write_text(text.replace('status: accepted','status: superseded'), encoding='utf-8')
            superseded = prompt_builder.select_unit(SELECTOR, root, 'W-001/step-1')
            self.assertEqual(superseded['decision_sources'][0]['status'], 'superseded')
            fresh = prompt_builder.build_prompt('executor', root, superseded, {}, 'German')
            self.assertNotIn('## Binding Decision', fresh)
            extra = source.with_name('0002-new-stop.md')
            extra.write_text(text.replace('ADR-0001','ADR-0002'), encoding='utf-8')
            plan = root/'docs/plans/0001-validate-profile.md'
            original = plan.read_text(encoding='utf-8')
            plan.write_text(original.replace('Decisions: [ADR-0001]','Decisions: [ADR-0002]'), encoding='utf-8')
            linked = prompt_builder.select_unit(SELECTOR, root, 'W-001/step-1')
            self.assertEqual([d['id'] for d in linked['decision_sources']], ['ADR-0002'])
            plan.write_text(original.replace('Decisions: [ADR-0001]','Decisions: []'), encoding='utf-8')
            self.assertEqual(prompt_builder.select_unit(SELECTOR,root,'W-001/step-1')['decision_sources'], [])

    def test_missing_or_ambiguous_source_produces_no_assignment(self):
        for missing in (True, False):
            with self.subTest(missing=missing), tempfile.TemporaryDirectory() as directory:
                root, source = self.setup_project(directory)
                if missing: source.unlink()
                else: source.with_name('0001-duplicate.md').write_bytes(source.read_bytes())
                with self.assertRaises(ValueError): prompt_builder.select_unit(SELECTOR,root,'W-001/step-1')

    def test_source_changed_after_projection_blocks_dispatch(self):
        with tempfile.TemporaryDirectory() as directory:
            root, source = self.setup_project(directory)
            run = prompt_builder.subprocess.run
            def change_after_selection(*args, **kwargs):
                result = run(*args, **kwargs)
                source.write_text(source.read_text(encoding='utf-8')+'\nChanged stop.\n',encoding='utf-8')
                return result
            with patch.object(prompt_builder.subprocess, 'run', side_effect=change_after_selection):
                with self.assertRaisesRegex(ValueError, 'source changed'):
                    prompt_builder.select_unit(SELECTOR, root, 'W-001/step-1')

    def test_full_closure_and_native_final_survive_reuse(self):
        with tempfile.TemporaryDirectory() as directory:
            root, source = self.setup_project(directory)
            context = prompt_builder.select_unit(SELECTOR,root,'W-001')
            report = 'status: done\nchanges: none\nchecks: retained complete evidence\n'
            reuse = prompt_builder.build_prompt('reviewer',Path(directory),context,{'executor_result':report},'German',reuse=True)
            self.assertIn(context['work_item']['context_text'].rstrip(), reuse)
            self.assertIn(report, reuse)
            self.assertIn(str(source.resolve()), reuse)
            self.assertNotIn('## Binding Decision', reuse)

if __name__ == '__main__': unittest.main()
