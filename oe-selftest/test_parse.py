import os
import unittest
from subprocess import Popen, PIPE
from patchtestdata import PatchTestInput as pti

class TestParse(unittest.TestCase):
    """ Test parsing using oe-selftest"""

    @classmethod
    def setUpClass(cls):
        cls.repodir = pti.repodir
        cls.bb_init_file = os.path.join(cls.repodir, 'oe-init-build-env')

    def test_bb_init_script(self):
        """ Check if the bb init script is an actual file"""
        self.assertTrue(os.path.isfile(self.bb_init_file))

    def test_oe_selftest_parse(self):
        """ A simple oe-selftest parse test"""
        cmds = [
            'cd %s' % self.repodir,
            'source %s' % self.bb_init_file,
            'bitbake-layers add-layer ../meta-selftest',
            'oe-selftest --run-tests bbtests.BitbakeTests.test_just_parse'
        ]
        sp = Popen(';'.join(cmds), cwd=self.repodir, shell=True, stdout=PIPE, stderr=PIPE)
        sp.communicate()
        self.assertEquals(0, sp.returncode)
