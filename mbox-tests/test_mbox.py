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
        cls.mbox = None
        item = Repo(pta.repodir, mbox=pta.mbox, series=pta.series, revision=pta.revision, commit=pta.commit, branch=pta.branch).item

        # the mbox can be either a file or an URL, so get content in both cases
        if item.startswith('http'):
            r = requests.get(item)
            cls.mbox = r.text
        else:
            with open(os.path.abspath(item)) as f:
                 cls.mbox = f.read()
        if not ''.join(cls.mbox).strip():
            raise(AssertionError, 'mbox should not be empty')

        (cls.keyvals, cls.chgfiles, cls.patchdiff) = ptsutils.get_patch_text_info(cls.mbox)

    def test_signed_off_by(self):
        """ Check Signed-off-by presence"""
        self.assertTrue('Signed-off-by' in TestMbox.keyvals, "Signed-off-by should be in mbox commit message")

    def test_signed_off_by_spelling(self):
        """ Check Signed-off-by correct spelling"""
        _keys = TestMbox.keyvals.keys()
        _lc_keys = set( ( k.lower() for k in _keys ) )
        _alt = set( ('signed-off-by', 'signed-off_by', 'signed_off-by', 'signed_off_by') )
        if not _alt.intersection(_lc_keys):
            raise unittest.SkipTest('Signed-off-by must be present to check its spelling')
        else:
            self.assertTrue('Signed-off-by' in _keys, "Signed-off-by seems to be mispelled")

    def test_upstream_status_spelling(self):
        """ Check Upstream-Status correct spelling"""
        _keys = TestMbox.keyvals.keys()
        _lc_keys = [k.lower() for k in _keys]
        if not ('upstream-status' in _lc_keys or 'upstream_status' in _lc_keys):
            raise unittest.SkipTest('Upstream-Status must be present to check its spelling')
        else:
            self.assertTrue('Upstream-Status' in _keys, "Upstream-Status seems to be mispelled")

    def test_upstream_status_value(self):
        """ Check Upstream-Status is if present"""
        if 'Upstream-Status' not in TestMbox.keyvals:
            raise unittest.SkipTest('Upstream-Status must be present to check its validity')
        else:
            for status in TestMbox.keyvals['Upstream-Status']:
                self.assertTrue([valid for valid in TestMbox.valid_upstream_status if valid == status], "Invalid Upstream-Status: %s" % status)

    def test_subject(self):
        """ Check Subject presence"""
        self.assertTrue('Subject' in TestMbox.keyvals, "Subject should be in mbox commit message")

    def test_subject_length(self):
        """ Check Subject length if present"""
        _key = 'Subject'
        if _key not in TestMbox.keyvals:
            raise unittest.SkipTest('Subject must be present to check its length')
        else:
            _val = TestMbox.keyvals[_key]
            self.assertTrue(len(_val) <= TestMbox.max_len, "%s too long, should be at most %s characters. Its value is '%s'" % (_key, TestMbox.max_len, _val))

    def test_description(self):
        """ Check Description presence"""
        # info: the Description field is obtained through pt-suites "ptsutils" module,
        #       from the Subject field. It is usually not a field that is present in
        #       mbox patch files.
        self.assertTrue('Description' in TestMbox.keyvals, "A Description should exist")
