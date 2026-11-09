"""Offline prompt-contract regressions; not proof of runtime permission enforcement."""
from pathlib import Path
import ast
import unittest

ROOT = Path(__file__).resolve().parents[2]

class ReviewModeContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = (ROOT / 'resources/review-modes.md').read_text()
        self.skills = {n: (ROOT / 'skills' / n / 'SKILL.md').read_text()
                       for n in ('egm-review', 'egm-review-loop', 'egm-resolve')}

    def test_all_entry_points_default_to_critique(self):
        for text in self.skills.values():
            self.assertIn('../../resources/review-modes.md', text)
            self.assertIn('Default to `ReviewMode: critique`', text)

    def test_critique_has_explicit_no_edit_exit(self):
        self.assertIn('Do not edit the target, code, configuration', self.contract)
        self.assertIn('only permitted writes are review/report artifacts', self.contract)
        self.assertIn('skip resolver edits', self.skills['egm-review-loop'])
        self.assertIn('return the annotated report without edits', self.skills['egm-resolve'])

    def test_full_is_scope_and_verification_bound(self):
        for text in ['Establish authorization for `EditScope`', 'agreed permitted checks',
                     'fresh independent reviewer', 'fixed, unverified']:
            self.assertIn(text, self.contract)

    def test_budgets_cover_nested_work(self):
        for text in ['MaxRounds', 'MaxAgentLaunches', 'MaxParallelAgents',
                     'retries', 'descendants', 'never silently reset counters']:
            self.assertIn(text, self.contract)
        self.assertIn('positive integer budgets', self.contract)

    def test_no_automatic_risk_acceptance(self):
        text = self.skills['egm-review']
        self.assertNotIn('residual findings as accepted trade-offs, auto-bind', text)
        self.assertIn('residual findings as open', text)
        self.assertIn('A contest alone stays open', self.skills['egm-review-loop'])

    def test_no_generic_proceed_edit_authorization(self):
        self.assertNotIn('User clicks "Proceed"', self.skills['egm-resolve'])
        self.assertIn('An ambiguous "proceed" does not switch modes', self.contract)

    def test_no_default_resolved_or_verified_claim(self):
        self.assertNotIn('Status: resolved', self.skills['egm-resolve'])
        self.assertNotIn('High-level architecture verified', self.skills['egm-review'])

    def test_reviewers_receive_read_only_contract(self):
        text = (ROOT / 'agents/synthesizer.md').read_text()
        self.assertIn('../resources/review-modes.md', text)
        self.assertIn('read-only constraints', text)
        self.assertIn('allocation to every', text)
        self.assertIn('budget', text)

    def test_no_merge_or_deploy_authority(self):
        self.assertIn('Never merge, enable auto-merge', self.contract)
        self.assertIn('deploy to PROD', self.contract)
        self.assertIn('not a technical sandbox', self.contract)

    def test_new_reference_ships_in_existing_bundle_glob(self):
        tree = ast.parse((ROOT / 'scripts/pack_plugin.py').read_text())
        strings = [n.value for n in ast.walk(tree)
                   if isinstance(n, ast.Constant) and isinstance(n.value, str)]
        self.assertIn('resources/*.md', strings)

    def test_skill_load_limit(self):
        for text in self.skills.values():
            self.assertLessEqual(len(text.split('---', 2)[2].strip().encode()), 24000)

if __name__ == '__main__':
    unittest.main()
