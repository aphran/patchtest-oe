from subprocess import Popen, PIPE
import os
from patchtestargs import PatchTestArgs as pta
from repo import Repo
import unittest
import requests
import re

def find_lines(lines, key):
    """ Returns the lines containing the key """
    _lines = []
    for line in lines:
        if line.find(key) != -1:
            _lines.append(line)
    return _lines

def parse_keyvals(patchfile, pattern=r'^([\w-]+):\s(.+)', endstr='---'):
    """ Parse a patch file for key value pairs. The optional pattern argument
        specifies how to find those key pairs (should return two match groups
        and the endstr argument specifies where to stop parsing."""

    with open(patchfile) as content_file:
        _current_key, _keyvals = None, {}
        for line in content_file:
            if line.startswith(endstr):
                break
            match = re.match(pattern, line)
            if match:
                groups = match.groups()
                _current_key = groups[0]
                _keyvals[_current_key] = groups[1].strip()
            elif _current_key:
                _keyvals[_current_key] += '%s' % line
    return _keyvals

@unittest.skipUnless(pta.mbox or pta.series, "requires the mbox or series argument")
class TestMbox(unittest.TestCase):
    """ A testcase containing (mbox formatted) patch related tests"""

    valid_upstream_status = ['Pending', 'Submitted', 'Accepted', 'Backport', 'Denied', 'Inappropriate']

    @classmethod
    def setUpClass(cls):
        cls.mbox = None
        mboxurl = Repo(pta.repodir, mbox=pta.mbox, series=pta.series, revision=pta.revision).mbox

        # the mbox can be either a file or an URL, so get content in both cases
        if mboxurl.startswith('http'):
            r = requests.get(mboxurl)
            cls.mbox = r.text.split('\n')
        else:
            with open(os.path.abspath(mboxurl)) as f:
                 cls.mbox = f.readlines()

    def test_signed_off_by(self):
        """ Check signed off by is present in each file """
        self.assertTrue(find_lines(TestMbox.mbox, 'Signed-off-by:'))

    def test_upsteam_status(self):
        """ Check upstream status is present in each file """
        for line in find_lines(TestMbox.mbox, 'Upstream-Status:'):
            self.assertTrue([valid for valid in TestMbox.valid_upstream_status if valid in line], "Invalid Upstream-Status: %s" % line)

    def test_summary_length(self):
        """ Check for a summary length"""
        _field_name = 'Subject'
        _field_min_len = 78
        fields = parse_keyvals(Test.Mbox.mbox)
        summary = fields[_field_name].splitlines()[(0)]
        self.assertTrue(len(summary) <= _field_min_len)
