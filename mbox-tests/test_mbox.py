import os
import re
import unittest
import requests
import sys
from patchtestdata import PatchTestInput as pti
from difflib import context_diff as diffs
from patchtestdata import PatchTestDataStore as ds
import logging
logger = logging.getLogger('patchtest')

@unittest.skipUnless(pti.mbox or pti.series, "requires the mbox or series argument")
class TestMbox(unittest.TestCase):
    """ A testcase containing (mbox formatted) patch related tests"""

    valid_upstream_status = ['Pending', 'Submitted', 'Accepted', 'Backport', 'Denied', 'Inappropriate']
    max_len = 78

    @classmethod
    def setUpClass(cls):
        cls.items = pti.repo.items

    def test_patch_format(self):
        """ Format check: patch is not empty and changes files"""
        # Checks for emptiness and changed files
        for _item in self.items:
            self.assertFalse(_item.is_empty, 'Mbox should not be empty')
            self.assertGreater(len(_item.changes), 0, "There should be changed files")

    def test_signed_off_by_check(self):
        """ Check Signed-off-by is present and spelled right"""
        for _item in self.items:
            _keys = _item.keyvals.keys()
            _lc_keys = set( ( k.lower() for k in _keys ) )
            _alt = set( ('signed-off-by', 'signed-off_by', 'signed_off-by', 'signed_off_by') )

            if not _alt.intersection(_lc_keys):
                raise AssertionError('Signed-off-by must be present to check its spelling')
            else:
                self.assertIn('Signed-off-by', _keys, "Signed-off-by seems to be mispelled")

    def test_upstream_status_check(self):
        """ Check Upstream-Status spelling and value if present"""
        for _item in self.items:
            _keys = _item.keyvals.keys()
            _lc_keys = [k.lower() for k in _keys]

            if not ('upstream-status' in _lc_keys or 'upstream_status' in _lc_keys):
                raise unittest.SkipTest('Upstream-Status must be present to validate it')
            else:
                self.assertTrue('Upstream-Status' in _keys, "Upstream-Status seems to be mispelled")
                for _st in _item.keyvals['Upstream-Status']:
                    self.assertTrue([valid for valid in TestMbox.valid_upstream_status if valid == _st], "Invalid Upstream-Status: %s" % _st)

    def test_subject_check(self):
        """ Check Subject presence, length, contents"""
        _key = 'Subject'
        for _item in self.items:
            if _key not in _item.keyvals:
                raise AssertionError('%s line missing' % _key)
            else:
                _val = ''.join(_item.keyvals[_key]).strip()
                self.assertLessEqual(len(_val), TestMbox.max_len, "%s too long, should be at most %s characters. Its value is '%s'" % (_key, TestMbox.max_len, _val))
                self.assertIn(':', _val, "%s doesn't include a colon, possibly missing component")

    def test_long_log(self):
        """ Check long log presence, contents"""
        _key = 'Description'
        for _item in self.items:
            _hasdesc = True if _key in _item.keyvals.keys() else False
            self.assertTrue(_hasdesc, "A long log should exist")
            if _hasdesc:
                self.assertTrue(''.join(_item.keyvals[_key]).strip(), 'Long log should not be empty')
                self.assertNotEquals(''.join(_item.keyvals[_key]).strip(), ''.join(_item.keyvals['Subject']).strip(), "Short and long logs should not be the same")

    def pretest_pylint(self):
        """ Run pylint on all modified python files, pre-merge"""
        self.common_pylint()

    def test_pylint(self):
        """ Run pylint on all modified python files, post-merge"""
        self.common_pylint()

    def common_pylint(self):
        """ Run pylint on all modified python files"""

        # Find changed python files
        pych = {}
        for _item in self.items:
            if _item.changes:
                for pf in [ _ for _ in _item.changes.modified_files if _.path.endswith('.py') ]:
                    pych[pf.path] = []
        if not pych:
            raise unittest.SkipTest('Python changes must exist to run pylint')

        # Run pylint on changed files and populate pych with findings
        from pylint import epylint as lint
        for pf in pych.keys():
            (pylo, _) = lint.py_run(pf, return_std=True)
            pych[pf] += [ line.strip() for line in pylo.readlines()[1:] ]

        # Store the changes in data store
        ds['pylint_new'] = set()
        for chglist in pych.values():
            for chg in chglist:
                if chg:
                    ds['pylint_new'].add(chg)
        
        # Show pylint issues
        logger.warn("\n----- Pylint issues in current test run -----")
        for _issue in ds['pylint_new']:
            logger.warn("  %s" % _issue)

        # Handle lint differences
        pylint_diff = set()
        if ds['pylint_old']:
            # Running post-merge test
            pylint_diff = ds['pylint_new'] - ds['pylint_old']

            # Printing new issues
            logger.warn("\n----- New Pylint issues -----")
            for _issue in pylint_diff:
                logger.warn("  %s" % _issue)

            self.assertEquals(len(pylint_diff), 0, "Found new pylint issues: %s" % str(pylint_diff))
        else:
            # Running pre-merge test
            ds['pylint_old'] = ds['pylint_new']
            self.assertEquals(len(ds['pylint_new']), 0, "There are pylint issues")
