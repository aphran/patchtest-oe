from subprocess import Popen, PIPE
import os
from patchtestargs import PatchTestArgs as pta
from repo import Repo
import unittest

def find_lines(path, key):
    """ Returns the lines containing the key """
    _lines = []
    with open(path) as f:
        for line in f.readlines():
            if line.find(key) != -1:
                _lines.append(line)
    return _lines

@unittest.skipUnless(pta.mbox, "requires the mbox argument")
class TestMbox(unittest.TestCase):
    """ A testcase containing (mbox formatted) patch related tests"""

    valid_upstream_status = ['Pending', 'Submitted', 'Accepted', 'Backport', 'Denied', 'Inappropriate']

    @classmethod
    def setUpClass(cls):
        # consider these variables monkey typed
        cls.mbox = os.path.abspath(pta.mbox)

    def test_patch_files(self):
        """ Check if the mbox items are actual files """
        self.assertTrue(os.path.isfile(TestMbox.mbox))

    def test_signed_off_by(self):
        """ Check signed off by is present in each file """
        self.assertTrue(find_lines(TestMbox.mbox, 'Signed-off-by:'))

    def test_upsteam_status(self):
        """ Check upstream status is present in each file """
        for line in find_lines(TestMbox.mbox, 'Upstream-Status:'):
            self.assertTrue([valid for valid in TestMbox.valid_upstream_status if valid in line], "Invalid Upstream-Status: %s" % line)

    # def test_summary_length(self):
    #     """ Check for a summary length"""
    #     lines = find_lines(TestMbox.mbox, 'Subject:')
    #     self.assertTrue(line, 'summary should be present')
    #     subject = lines[0]
    #     liens.split(':')
    #     #for file in cls.mbox:
    #     	#	summary = None #what do I do here
    #     	#	check if patchwork has this
    #     	self.assertTrue(True)

