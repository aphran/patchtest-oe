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

def parse_keyvals(lines, pattern=r'^([\w-]+):\s(.+)', endstr='---'):
    """ Parse a patch file for key value pairs. The optional pattern argument
        specifies how to find those key pairs (should return two match groups
        and the endstr argument specifies where to stop parsing."""

    _keyvals = {}
    _text = ''
    for line in lines:
        if line.startswith(endstr):
            break
        _text += line
    return _text.split(pattern)

@unittest.skipUnless(pta.mbox or pta.series, "requires the mbox or series argument")
class TestMbox(unittest.TestCase):
    """ A testcase containing (mbox formatted) patch related tests"""

    valid_upstream_status = ['Pending', 'Submitted', 'Accepted', 'Backport', 'Denied', 'Inappropriate']
    field_max_len = 78

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
        if not ''.join(cls.mbox).strip():
            raise(AssertionError, 'mbox should not be empty')

    def test_signed_off_by(self):
        """ Check signed off by is present in each file """
        self.assertTrue(find_lines(TestMbox.mbox, 'Signed-off-by:'), "signed-off-by line missing or incorrect")

    def test_upsteam_status(self):
        """ Check upstream status is present in each file """
        for line in find_lines(TestMbox.mbox, 'Upstream-Status:'):
            self.assertTrue([valid for valid in TestMbox.valid_upstream_status if valid in line], "Invalid Upstream-Status: %s" % line)

    def test_summary_length(self):
        """ Check for a summary length"""
        _field = 'Subject: '
        _max = TestMbox.field_max_len
        summary = ' '.join(find_lines(TestMbox.mbox, _field))
        summary = re.sub('%s|\[[\w_/ -]*\] ' % _field, '',summary)
        print '<<Summary found: %s>>' % summary
        self.assertTrue(len(summary) <= _max, "summary too long, it should be at most %s characters. The summary is '%s'" % (TestMbox.field_max_len, summary))

    def test_description(self):
        """ Check description is present"""
        field_name = 'Subject' # Description lines follow Subject
        fields = parse_keyvals(TestMbox.mbox)
        #description = 'asd\nqwe\nqeyqwuiey' #' '.join(fields[field_name].splitlines()[1:]).strip()
        description = fields[field_name]
        print '<< Description found: %s >>' % description
        self.assertTrue(description)
