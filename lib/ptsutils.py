import re
from patchwork_parser import parse_patch
import unidiff

def append_new(d, k, v):
    if k in d:
        d[k].append(v)
    else:
        d[k] = [v]

def parse_keyvals(text, pattern='^([\w-]+):\s+(.*)$'):
    """ Parse a patch file or fragment for key-value pairs. The optional pattern
        argument specifies how to find those key-value pairs (should return two
        match groups)
    """
    keyvals = {}
    for _line in [ _.strip() for _ in text.splitlines()[1:] ]:
        _m = re.match(pattern, _line)
        if _m and _m.groups():
            _k, _v = _m.groups()
            append_new(keyvals, _k, _v)
        else:
            if _line:
                append_new(keyvals, 'Description', _line)
    return keyvals

def parse_for_files(text, pattern='^[ ]*([\w /_.-]+)[ ]+[|].*', end='.*file[\w]?[ ]changed'):
    """ Parse a patch file or fragment for changed files. The optional pattern
        argument specifies how to find those key-value pairs (should return two
        match groups); the endstr argument specifies where to stop parsing.
    """
    files = []
    files_chunk = re.split(end, text)[0]
    for line in files_chunk.splitlines():
        m = re.match(pattern, line)
        if m and m.groups():
            files.append(m.groups()[0].strip())
    return files

def parse_file_hunks(text):
    return unidiff.PatchSet(text)

#def parse_file_hunks(text):
#    """ From a patch diff buffer, parse hunk sections and return them as grouped tuples"""
#    _hunks = []
#    _pattern = '\n--- a/[\w /_.-]+.*\n[+]{3} b/([\w /_.-]+).*\n@@ [\d,+-]+ [+-]([\d]+),([\d]+) @@.*'
#    _len = 3
#    _match = re.search(_pattern, text)
#    if _match:
#        _groups = _match.groups()
#        if _groups:
#            _hunks = zip(*[iter(_groups)] * _len)
#    return _hunks

def read_file(f):
    text = None
    with open(f) as fb:
        text = fb.read()
    return text

def get_patch_text_info(patchtext):
    keyvals = {}
    hunks = None
    patchbuf = cmt_buf = ''
    cmt_seps = ('---', 'diff')
    patchbuf, cmt_buf = parse_patch(patchtext)
    cmt_head = cmt_buf

    for _sep in cmt_seps:
        sep_index = cmt_buf.find(_sep)
        if sep_index >= 0:
            cmt_head = cmt_buf[:sep_index]
            break

    keyvals = parse_keyvals(cmt_head)
    
    hunks = parse_file_hunks(patchtext)
    from pprint import pprint; pprint(hunks)

    return (keyvals, patchbuf, hunks)

def get_patch_info(patchfile):
    patchtext = read_file(patchfile)
    return get_patch_text_info(patchtext)
