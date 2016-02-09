import os
import re
import unittest
import requests
from patchtestargs import PatchTestArgs as pta
from repo import Repo

# The "ptsutils" module is needed, add it from the usual location
import sys
_libdir = '../lib'
_libpath = os.path.realpath(os.path.join(os.path.dirname(__file__), _libdir))
sys.path.insert(0, _libpath)
import ptsutils

@unittest.skipUnless(pta.mbox or pta.series, "requires the mbox or series argument")
class TestMbox(unittest.TestCase):
    """ A testcase containing (mbox formatted) patch related tests"""

    valid_upstream_status = ['Pending', 'Submitted', 'Accepted', 'Backport', 'Denied', 'Inappropriate']
    max_len = 78

    @classmethod
    def setUpClass(cls):
        cls.items = Repo(pta.repodir, mbox=pta.mbox, series=pta.series, revision=pta.revision, commit=pta.commit, branch=pta.branch).items

        for _item in cls.items:
            if _item.is_empty:
                raise(AssertionError, 'mbox should not be empty')
            else:
                (_item.keyvals, _item.chgfiles, _item.patchdiff, _item.hunks) = ptsutils.get_patch_text_info(_item.contents)

    def test_signed_off_by(self):
        """ Check Signed-off-by presence"""
        for _item in self.items:
            self.assertTrue('Signed-off-by' in _item.keyvals, 'Signed-off-by absent from commit message')

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
        # info: the Description field is obtained through pt-suites "ptsutils" module,
        #       from the Subject field. It is usually not a field that is present in
        #       mbox patch files.
        for _item in self.items:
            self.assertTrue('Description' in _item.keyvals, "A Description should exist")

#    def test_hunks(self):
#        """ Obtain changed python lines, compare with pylint"""
#        _hunks = TestMbox.hunks
#        if _hunks:
#            for _ in _hunks:
#                print(str(_))
#            self.assertTrue(True, "All good, sailor!")
#        else:
#            raise AssertionError
