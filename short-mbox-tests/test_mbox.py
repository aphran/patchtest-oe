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

    def test_patch_format(self):
        """ Check patch has valid formatting """
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
        """ Check Subject presence and length"""
        _key = 'Subject'
        for _item in self.items:
            if _key not in _item.keyvals:
                raise AssertionError('%s line missing' % _key)
            else:
                _val = _item.keyvals[_key]
                self.assertLessEqual(len(_val), TestMbox.max_len, "%s too long, should be at most %s characters. Its value is '%s'" % (_key, TestMbox.max_len, _val))

    def test_description(self):
        """ Check Description presence"""
        for _item in self.items:
            _hasdesc = True if 'Description' in _item.keyvals else False
            self.assertTrue(_hasdesc, "A Description should exist")
            if _hasdesc:
                self.assertTrue(''.join(_item.keyvals['Description']).strip(), 'Description should not be empty')

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
