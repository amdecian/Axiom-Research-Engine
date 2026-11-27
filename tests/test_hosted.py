import unittest
from scripts.hosted import validate_event, PROFILES

class HostedTests(unittest.TestCase):
    def test_public_only(self):
        event={'repository':{'private':False,'visibility':'public'}}
        validate_event(event,'push','refs/heads/main','github-hosted')
        validate_event(event,'pull_request','refs/pull/1/merge','github-hosted')
        for bad in ({},{'repository':{'private':True}},{'repository':{'private':False,'visibility':'internal'}}):
            with self.assertRaises(ValueError): validate_event(bad,'push','refs/heads/main','github-hosted')
    def test_reject_wrong_scope(self):
        event={'repository':{'private':False}}
        for name,ref,runner in [('schedule','refs/heads/main','github-hosted'),('workflow_dispatch','refs/heads/feature','github-hosted'),('push','refs/heads/main','self-hosted')]:
            with self.assertRaises(ValueError): validate_event(event,name,ref,runner)
    def test_profiles(self):
        self.assertEqual(set(PROFILES),{'quick','loop-replay','pattern-regression','portal-check'})
        self.assertTrue(all(0<t<=300 for _,t in PROFILES.values()))
