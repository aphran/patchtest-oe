from base import PatchTestBase
import os
from subprocess import Popen, PIPE

class TestParse(PatchTestBase):
    @classmethod
    def setUpClass(cls):
        super(cls, TestParse).setUpClass()
        cls.bb_init_file = os.path.join(cls.repo.repodir, 'oe-init-build-env')
        cls.bb_parse_cmd = 'bitbake -p'

    def bb_init(self):
        self.cmd = 'cd %s; source %s; %s' % (self.repo.repodir, self.bb_init_file, self.bb_parse_cmd)
        self.sp = Popen(self.cmd, cwd=self.repo.repodir, shell=True, stdout=PIPE, stderr=PIPE)
        out, err = self.sp.communicate()
        #print out, err

    def test_bb_init_script(self):
        """ Check if the bb init script is an actual file"""
        self.assertTrue(os.path.isfile(self.bb_init_file))

    def test_bb_parse(self):
        """ A simple bitbake parse test"""
        self.bb_init()
        self.assertFalse(self.sp.returncode)
