"""Exercise real packaged helpers across a bounded, simulated workflow."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

from test_contract import PACKAGE, SUITE_ROOT, _builder


class LifecycleTests(unittest.TestCase):
    def test_select_dispatch_review_correct_continue_and_close(self):
        fixture = SUITE_ROOT / 'members/scoville-plan/development/tests/fixtures/valid-profile'
        validator = SUITE_ROOT / 'members/scoville-plan/scoville-plan/scripts/validate_profile.py'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'project'
            shutil.copytree(fixture, root)
            env = {**os.environ, 'CODEX_THREAD_ID': '01a0e778-0c80-7660-b8b9-c8ce59a9fed4'}
            def run(script, *args, good=True):
                result = subprocess.run([sys.executable, str(script), *map(str,args)],
                    env=env, capture_output=True, text=True, encoding='utf-8')
                if good:
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                else:
                    self.assertNotEqual(result.returncode, 0)
                return result.stdout
            def file(name, text):
                target=root/name;target.write_text(text,encoding='utf-8');return target
            self.assertTrue(json.loads(run(validator,'--root',root,'--format','json'))['valid'])
            pair=json.loads(run(PACKAGE/'scripts/resolve_model_pair.py','--project-root',root,
                                '--role','executor','--route','medium'))
            self.assertIn('model',pair);self.assertIn('thinking',pair)
            builder=PACKAGE/'scripts/build_dispatch_prompt.py'
            args=['--project-root',root,'--unit','W-001/steps-1-2']
            executor=run(builder,*args,'--role','executor')
            self.assertIn('return_to_thread_id='+env['CODEX_THREAD_ID'],executor)
            result=file('worker.txt','completed: café ✓ changed; targeted checks passed; live use unverified.')
            scope=file('scope.txt','Review only the scoped change in example.py and its acceptance; read-only.')
            review=run(builder,*args,'--role','reviewer','--executor-result',result,'--supplemental-context',scope)
            self.assertIn(result.read_text(encoding='utf-8'),review)
            self.assertIn(scope.read_text(encoding='utf-8'),review)
            finding=file('review.txt','changes_requested: example.py drops a space; preserve it and test adjacency.')
            correction=run(builder,*args,'--role','executor','--reviewer-result',finding,'--supplemental-context',scope)
            self.assertIn(finding.read_text(encoding='utf-8'),correction)
            handoff=file('handoff.txt','Finished implementation and checks of step 1. Only final adjacency test remains.')
            successor=run(builder,*args,'--role','executor','--context-handoff',handoff,
                          '--predecessor-thread-id','01a0ebd5-922f-7ff0-88ba-bfe0699c8313',
                          '--supplemental-context',scope)
            self.assertIn(handoff.read_text(encoding='utf-8'),successor)
            self.assertNotIn('## Work Item context',successor)
            self.assertIn('01a0ebd5-922f-7ff0-88ba-bfe0699c8313',successor)
            # The Plan writer owns these transitions; helpers only inspect them.
            plan=root/'docs/plans/0001-validate-profile.md'
            text=plan.read_text(encoding='utf-8')
            text=text.replace('current_item: W-001','current_item: W-002')
            text=text.replace('Status: in_progress','Status: done',1)
            text=text.replace('Evidence: []','Evidence: Simulated acceptance observed.',1)
            text=text.replace('Next action: Run the structural validator.\n','')
            plan.write_text(text,encoding='utf-8')
            self.assertTrue(json.loads(run(validator,'--root',root,'--format','json'))['valid'])
            # Ordinary successor can be selected while blocked, not started.
            text=text.replace('### W-002 Validate relationships\n\nStatus: todo\nDepends on: [W-001]\nBlocked by: []',
                              '### W-002 Validate relationships\n\nStatus: todo\nDepends on: [W-001]\nBlocked by: [EXT-ACCESS]')
            plan.write_text(text,encoding='utf-8')
            self.assertTrue(json.loads(run(validator,'--root',root,'--format','json'))['valid'])
            text=text.replace('Blocked by: [EXT-ACCESS]','Blocked by: []')
            text=text.replace('Status: todo','Status: done').replace('Evidence: []','Evidence: Simulated final acceptance.')
            text=text.replace('Next action: Wait for W-001 acceptance evidence.\n','')
            text=text.replace('status: active','status: completed').replace('current_item: W-002\n','')
            plan.write_text(text,encoding='utf-8')
            index=root/'PROJECT_INDEX.md'
            index.write_text(index.read_text(encoding='utf-8').replace('active_plan: PLAN-0001','active_plan: null'),encoding='utf-8')
            self.assertTrue(json.loads(run(validator,'--root',root,'--format','json'))['valid'])
            run(PACKAGE/'scripts/select_context.py','--root',root,'--format','json',good=False)

    def test_no_python_fallback_is_only_in_general_package(self):
        for profile, expected in [('general',True),('codex',False)]:
            config=_builder.load(SUITE_ROOT,profile)
            member=next(m for m in config['members'] if m['name']=='scoville-plan')
            payload=_builder.payload(SUITE_ROOT,member,config)
            for name in ['fallbacks/validate_profile-fallback.md','fallbacks/select_context-fallback.md']:
                self.assertEqual(any(path.endswith('/'+name) for path in payload),expected)
            if not expected:
                self.assertNotIn(b'fallbacks/validate_profile-fallback.md',payload['scoville-plan/SKILL.md'])


if __name__=='__main__':
    unittest.main()
