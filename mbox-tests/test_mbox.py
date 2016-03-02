import os
import re
import unittest
import requests
from patchtestdata import PatchTestInput as pti
import sys

@unittest.skipUnless(pti.mbox or pti.series, "requires the mbox or series argument")
class TestMbox(unittest.TestCase):
    """ A testcase containing (mbox formatted) patch related tests"""

    valid_upstream_status = ['Pending', 'Submitted', 'Accepted', 'Backport', 'Denied', 'Inappropriate']
    max_len = 78

    @classmethod
    def setUpClass(cls):
        cls.items = pti.repo.items

        for _item in cls.items:
            if _item.is_empty:
                raise(AssertionError, 'mbox should not be empty')

    def test_signed_off_by(self):
        """ Check Signed-off-by presence"""
        for _item in self.items:
            _keyvals = _item.keyvals
            _signoff = True if 'Signed-off-by' in _keyvals else False
            self.assertTrue(_signoff, 'Signed-off-by absent from commit message')
            if _signoff:
                self.assertTrue(''.join(_keyvals['Signed-off-by']).strip(), 'Singed-off-by should not be empty')

    def test_signed_off_by_spelling(self):
        """ Check Signed-off-by correct spelling"""
        for _item in self.items:
            _keys = _item.keyvals.keys()
            _lc_keys = set( ( k.lower() for k in _keys ) )
            _alt = set( ('signed-off-by', 'signed-off_by', 'signed_off-by', 'signed_off_by') )
            if not _alt.intersection(_lc_keys):
                raise unittest.SkipTest('Signed-off-by must be present to check its spelling')
            else:
                self.assertTrue('Signed-off-by' in _keys, "Signed-off-by seems to be mispelled")

    def test_upstream_status_spelling(self):
        """ Check Upstream-Status correct spelling"""
        for _item in self.items:
            _keys = _item.keyvals.keys()
            _lc_keys = [k.lower() for k in _keys]
            if not ('upstream-status' in _lc_keys or 'upstream_status' in _lc_keys):
                raise unittest.SkipTest('Upstream-Status must be present to check its spelling')
            else:
                self.assertTrue('Upstream-Status' in _keys, "Upstream-Status seems to be mispelled")

    def test_upstream_status_value(self):
        """ Check Upstream-Status is if present"""
        for _item in self.items:
            if 'Upstream-Status' not in _item.keyvals:
                raise unittest.SkipTest('Upstream-Status must be present to check its validity')
            else:
                for _st in _item.keyvals['Upstream-Status']:
                    self.assertTrue([valid for valid in TestMbox.valid_upstream_status if valid == _st], "Invalid Upstream-Status: %s" % _st)

    def test_subject(self):
        """ Check Subject presence"""
        for _item in self.items:
            self.assertTrue('Subject' in _item.keyvals, "Subject should be in mbox commit message")

    def test_subject_length(self):
        """ Check Subject length if present"""
        for _item in self.items:
            _key = 'Subject'
            if _key not in _item.keyvals:
                raise unittest.SkipTest('Subject must be present to check its length')
            else:
                _val = _item.keyvals[_key]
                self.assertTrue(len(_val) <= TestMbox.max_len, "%s too long, should be at most %s characters. Its value is '%s'" % (_key, TestMbox.max_len, _val))

    def test_description(self):
        """ Check Description presence"""
        for _item in self.items:
            _hasdesc = True if 'Description' in _item.keyvals else False
            self.assertTrue(_hasdesc, "A Description should exist")
            if _hasdesc:
                self.assertTrue(''.join(_item.keyvals['Description']).strip(), 'Description should not be empty')

    def test_changes_exist(self):
        """ Check there are changed files"""
        for _item in self.items:
            changes = _item.changes
            self.assertTrue(len(changes) > 0, "There should be changed files")

    def test_pylint(self):
        """ Obtain changed python lines, compare with pylint"""
        pych = {}
        for _item in self.items:
            if _item.changes:
                for pf in [ _ for _ in _item.changes.modified_files if _.path.endswith('.py') ]:
                    pych[pf.path] = []
        if not pych:
            raise unittest.SkipTest('Python changes must exist to run pylint')
        else:
            from pylint import epylint as lint
            for pf in pych.keys():
                (pylo, _) = lint.py_run(pf, return_std=True)
                pych[pf] += [ line.strip() for line in pylo.readlines()[1:] ]
                #for line in pych[pf]:
                #    print("%s" % line)
                self.assertFalse([pf for pf in pych.keys() if len(pych[pf]) > 0 ],"Any pylint output causes a failure")
