#!/usr/bin/env python

import re

def parse_keyvals(patchfile, pattern='\n([\w-]+):\s', endstr='---'):
    """ Parse a patch file for key value pairs. The optional pattern argument
        specifies how to find those key pairs (should return two match groups
        and the endstr argument specifies where to stop parsing.
    """
    keyvals = {}
    with open(patchfile) as pf:
        text = pf.read()
    text_chunks = text.split(endstr)
    dict_chunks = re.split(pattern, text_chunks[0])
    keyvals = dict(zip(dict_chunks[1::2], dict_chunks[2::2]))
    return [keyvals, text_chunks[1:]]

def pw_parse(patchfile):
    from parser import parse_patch
    keyvals = ()
    with open(patchfile) as pf:
        text = pf.read().decode('utf-8')
    keyvals = parse_patch(text)
    return keyvals

if __name__ == '__main__':

    from pprint import pprint
    from sys import argv

    patchfile = argv[1]
    print 'Received file: <%s>' % patchfile

    keyvals = parse_keyvals(patchfile)
    pprint(keyvals)

    print '\n\n'

    keyvals = pw_parse(patchfile)
    pprint(keyvals)
