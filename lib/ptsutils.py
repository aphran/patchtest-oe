import re
from patchwork_parser import parse_patch

def append_new(d, k, v):
    if k in d:
        d[k].append(v)
    else:
        d[k] = [v]

def parse_keyvals(text, pattern='\n([\w-]+):\s'):
    """ Parse a patch file or fragment for key-value pairs. The optional pattern
        argument specifies how to find those key-value pairs (should return two
        match groups); the endstr argument specifies where to stop parsing.
    """
    keyvals = {}
    dict_chunks = re.split(pattern, text)
    for key, val in zip(dict_chunks[1::2], dict_chunks[2::2]):
        for line in val.strip().splitlines():
            if line: append_new(keyvals, key, line)

    # handle Subject and description
    key = 'Subject'
    if key in keyvals:
        sublines = keyvals[key]
        keyvals[key] = [sublines[0]]
        keyvals['Description'] = sublines[1:]

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

def read_file(f):
    text = None
    with open(f) as fb:
        text = fb.read().decode('utf-8')
    return text

def get_patch_text_info(patchtext):
    keyvals = {}
    chgfiles = []
    patchbuf = ''
    cmt_head = ''
    cmt_tail = ''

    cmt_sep = '---'

    patchbuf, cmt_buf = parse_patch(patchtext)

    sep_index = cmt_buf.find(cmt_sep) or None
    if sep_index >= 0:
        cmt_head = cmt_buf[:sep_index]
        cmt_tail = cmt_buf[sep_index + len(cmt_sep) - 1:]

    keyvals = parse_keyvals(cmt_head)
    chgfiles = parse_for_files(cmt_tail)

    return (keyvals, chgfiles, patchbuf)

def get_patch_info(patchfile):
    patchtext = read_file(patchfile)
    return get_patch_text_info(patchtext)
