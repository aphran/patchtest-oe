from subprocess import Popen, PIPE
import os
import patchtest
import unittest

class TestMbox(unittest.TestCase):
    """ A testcase containing (mbox formatted) patch related tests"""
    @classmethod
    def setUpClass(cls):
        # consider these variables monkey typed
        cls.mbox = patchtest.PatchTestArgs.mbox

	def find_key(path, key):
		""" From oelint.bbclass, finds key in path (file)"""
		ret = True
		f = file('%s' % path, mode = 'r')
		line = f.readline()
		while line:
			if line.find(key) != -1:
				ret = False
			line = f.readline()
		f.close()
		return ret

    def test_patch_files(self):
        """ Check if the mbox items are actual files"""
        for file in cls.mbox:
            self.assertTrue(os.path.isfile(file))

    def test_signed_off_by(self):
        """ Check signed off by is present in each file"""
        for file in cls.mbox:
            self.assertTrue(find_key(os.path.abspath(file), 'Signed-off-by: '))

    def test_upsteam_status(self):
        """ Check upstream status is present in each file"""
        for file in cls.mbox:
            self.assertTrue(find_key(os.path.abspath(file), 'Upstream-Status: '))

    def test_summary_length(self):
        """ Check for a minimum summary length"""
        #for file in cls.mbox:
		#	summary = None #what do I do here
		#	check if patchwork has this
		self.assertTrue(True)

