from subprocess import Popen, PIPE
import os
from patchtestargs import PatchTestArgs as pta
from repo import Repo
import unittest
import requests
import re
import mailbox
import tempfile

def split_payload(payload):
    """ Split an mbox payload"""

    pattern='^([\w-]+): (.+)$'
    endstr='---'
    _text = ''
    _keyvals = {}

    _st = {
        'desc'  : 0,
        'fields': 1,
        'files' : 2,
        'patch' : 3
    }
    _status = _st['desc']

    for line in payload.splitlines():
        if _status == _st['desc']:
            match = re.match(pattern, line):
            if match:
                match_groups = match.groups()
                _keyvals[match_groups[0]] = match_groups[1]
                
                
        _text += '\n' + line
    chunks = re.split(pattern, _text)
    pprint(chunks)
    ret = dict(zip(chunks[1::2], chunks[0::2]))
    pprint(ret)
    return ret

    return ['a', 'b', 'c']

def parse_mbox(mbox):
    """ Parse a patch file, returning a list containing: a dictionary of key - 
        value pairs, a message string, a list of changed files and a patch diff
        string, which is the rest of the original mbox formatted message.
        This function takes a mailbox.mbox instance
    """
    _ret = []
    _keyvals = {}

    _pay = ''
    for msg in mbox:
        if msg.is_multipart():
            for part in msg.get_payload():
                _keyvals += part.items()
                _pay += part.get_payload(decode=True)
        else:
            _keyvals = msg.items()
            _pay = msg.get_payload(decode=True)

    _ret = [ _keyvals, split_payload(_pay) ]
    return _ret

@unittest.skipUnless(pta.mbox or pta.series, "requires the mbox or series argument")
class TestMbox(unittest.TestCase):
    """ A testcase containing (mbox formatted) patch related tests"""

    valid_upstream_status = ['Pending', 'Submitted', 'Accepted', 'Backport', 'Denied', 'Inappropriate']
    field_max_len = 78

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

        # create a temp file with mbox contents, parse it using both the 
        # mailbox.mbox methods and the parse_mbox function

        tmpf = tempfile.NamedTemporaryFile()
        with open(tmpf.name, 'w') as f:
            f.write(cls.mbox)
        mboxobj = mailbox.mbox(tmpf.name)
        cls.parsed_mbox = parse_mbox(mboxobj)

#    def test_signed_off_by(self):
#        """ Check signed off by is present in each file """
#        self.assertTrue(find_lines(TestMbox.mbox, 'Signed-off-by:'), "signed-off-by line missing or incorrect")
#
#    def test_upsteam_status(self):
#        """ Check upstream status is present in each file """
#        for line in find_lines(TestMbox.mbox, 'Upstream-Status:'):
#            self.assertTrue([valid for valid in TestMbox.valid_upstream_status if valid in line], "Invalid Upstream-Status: %s" % line)
#
#    def test_summary_length(self):
#        """ Check for a summary length"""
#        _field = 'Subject: '
#        _max = TestMbox.field_max_len
#        summary = ' '.join(find_lines(TestMbox.mbox, _field))
#        summary = re.sub('%s|\[[\w_/ -]*\] ' % _field, '',summary)
#        print '<<Summary found: %s>>' % summary
#        self.assertTrue(len(summary) <= _max, "summary too long, it should be at most %s characters. The summary is '%s'" % (TestMbox.field_max_len, summary))
#
#    def test_description(self):
#        """ Check description is present"""
#        field_name = 'Subject' # Description lines follow Subject
#        fields = parse_keyvals(TestMbox.mbox)
#        #description = 'asd\nqwe\nqeyqwuiey' #' '.join(fields[field_name].splitlines()[1:]).strip()
#        description = fields[field_name]
#        print '<< Description found: %s >>' % description
#        self.assertTrue(description)

    def test_dummy_mbox(self):
        print TestMbox.parsed_mbox
        assert True
