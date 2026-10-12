"""Real selector-to-child projection: one exact Step, unchanged findings, full closure."""
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
    def test_communication_language_preserves_literal_user_request(self):
        request = 'User request: “Bitte kurz auf Deutsch beantworten.”'
        prompt = prompt_builder.build_prompt('explorer', Path('/project'), {}, {'supplemental_context': request}, 'German')
        delivery = prompt_builder.communication_rule('German')
        self.assertEqual(prompt.count(request), 1)
        self.assertEqual(prompt.count(delivery), 1)
        self.assertLess(prompt.index(request), prompt.index('## Communication'))
        self.assertLess(prompt.index(delivery), prompt.index('On user stop,'))
        self.assertIn('Communication language: German.', delivery)
        self.assertIn('natural-language text in result fields', delivery)

    def prepare(self, directory, ending):
        root = Path(directory) / 'project'
        shutil.copytree(SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile', root)
        path = root / 'docs/plans/0001-validate-profile.md'
        text = path.read_text(encoding='utf-8').replace(
            '1. Read the canonical files.\n2. Check the local record shapes.',
            '1. [status: done] OUTSIDE-FIRST.\n'
            '2. [status: in_progress] [execute: reasoning=high] Preserve café and `中文`.\n'
            '3. OUTSIDE-THIRD.\n4. OUTSIDE-LAST.').replace('Steps:\n', 'Instructions: Preserve exact literals.\nSteps:\n', 1)
        text = text.replace('Evidence: []', 'Evidence: HISTORY-ONLY', 1)
        path.write_bytes(text.replace('\n', ending).encode('utf-8'))
        return root

    def test_original_step_and_binding_context_stay_identical_with_findings(self):
        for ending in ('\n', '\r\n'):
            with self.subTest(ending=repr(ending)), tempfile.TemporaryDirectory() as directory:
                root = self.prepare(directory, ending)
                before = {p:p.read_bytes() for p in root.rglob('*') if p.is_file()}
                context = prompt_builder.select_unit(PACKAGE / 'scripts/select_context.py', root, 'W-001/step-2')
                item=context['work_item']; contexts=[]
                findings='changes_requested: owner.py line4; missing trim; affected Step2.'
                report='done; changed_paths: owner.py; baseline: before.txt; checks: owner test passed.'
                for role, inputs in [('executor',{}),('executor',{'reviewer_result':findings}),
                                     ('reviewer',{'executor_result':report}),
                                     ('reviewer',{'executor_result':report,'reviewer_result':findings}),
                                     ('explorer',{'supplemental_context':'Question about this Step.'})]:
                    prompt=prompt_builder.build_prompt(role,root,context,inputs, 'German')
                    embedded=prompt.split('## Work Item context\n',1)[1].split('\n## ',1)[0].split('On user stop,',1)[0]
                    contexts.append(embedded.rstrip())
                    for key in ('header','status','depends_on','blocked_by','decisions','outcome','acceptance'):
                        self.assertIn(item[key],embedded)
                    self.assertIn('Instructions: Preserve exact literals.',embedded)
                    self.assertIn('Steps:\n'+item['source_text'],embedded)
                    for excluded in ('OUTSIDE-FIRST','OUTSIDE-THIRD','OUTSIDE-LAST','HISTORY-ONLY','Evidence:','Next action:'):
                        self.assertNotIn(excluded,embedded)
                    for key,value in inputs.items():
                        self.assertIn('## '+key+'\n'+value,prompt)
                        self.assertNotIn(value,embedded)
                self.assertEqual(len(set(contexts)),1)
                for role,inputs in [('executor',{'supplemental_context':'Rewritten Step.'}),
                                    ('reviewer',{'executor_result':report,'supplemental_context':'Rewritten Step.'})]:
                    with self.assertRaisesRegex(ValueError,'unknown role input'):
                        prompt_builder.build_prompt(role,root,context,inputs, 'German')
                self.assertEqual(before,{p:p.read_bytes() for p in root.rglob('*') if p.is_file()})

    def test_missing_binding_fields_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root=self.prepare(directory,'\n')
            context=prompt_builder.select_unit(PACKAGE/'scripts/select_context.py',root,'W-001/step-2')
            del context['work_item']['context_text']
            self.assertIn('2. [status:',prompt_builder.work_item_context(context['work_item']))
            for field in ('unit','source_text','header','status','depends_on','blocked_by','decisions','outcome','acceptance','instructions'):
                broken=copy.deepcopy(context);broken['work_item'][field]=None
                with self.subTest(field=field),self.assertRaises(ValueError):
                    prompt_builder.build_prompt('executor',root,broken,{}, 'German')

    def test_whole_closure_keeps_all_steps_and_ranges_cannot_execute(self):
        with tempfile.TemporaryDirectory() as directory:
            root=self.prepare(directory,'\n')
            context=prompt_builder.select_unit(PACKAGE/'scripts/select_context.py',root,'W-001')
            report='done; changed_paths: owner.py; checks: owner test passed.'
            prompt=prompt_builder.build_prompt('reviewer',root,context,{'executor_result':report}, 'German')
            self.assertEqual(prompt.count(context['work_item']['context_text'].rstrip()),1)
            for literal in ('EVERY original Step','FULL Work Item Acceptance','OUTSIDE-FIRST','OUTSIDE-LAST'):
                self.assertIn(literal,prompt)
            with self.assertRaises(ValueError):
                prompt_builder.build_prompt('executor',root,context,{}, 'German')
            with self.assertRaises(ValueError):
                prompt_builder.select_unit(PACKAGE/'scripts/select_context.py',root,'W-001/steps-2-3')
            question=prompt_builder.build_prompt('explorer',root,{}, {'supplemental_context':'Question without Plan.'}, 'German')
            self.assertNotIn('## Work Item context',question)

if __name__=='__main__': unittest.main()
