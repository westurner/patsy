# This file is part of Charlton
# Copyright (C) 2012 Nathaniel Smith <njs@pobox.com>
# See file COPYING for license information.

# This file contains compatibility code for supporting old versions of Python
# and numpy. (If we can concentrate it here, hopefully it'll make it easier to
# get rid of weird hacks once we drop support for old versions).

##### Numpy

import os
# To force use of the compat code, set this env var to a non-empty value:
modern_ok = not os.environ.get("CHARLTON_FORCE_COMPAT")

# The *_indices functions were added in numpy 1.4
import numpy as np
if modern_ok and hasattr(np, "triu_indices"):
    from numpy import triu_indices
    from numpy import tril_indices
    from numpy import diag_indices
else:
    def triu_indices(n):
        return np.triu(np.ones((n, n))).nonzero()
    def tril_indices(n):
        return np.tril(np.ones((n, n))).nonzero()
    def diag_indices(n):
        return (np.arange(n), np.arange(n))

##### Python standard library

# The Python license requires that all derivative works contain a "brief
# summary of the changes made to Python". Both for license compliance, and for
# our own sanity, therefore, please add a note at the top of any snippets you
# add here explaining their provenance, any changes made, and what versions of
# Python require them:

# Copied unchanged from Python 2.7.3's re.py module; all I did was add the
# import statements at the top.
# This code seems to be included in Python 2.5+.
import re
if modern_ok and hasattr(re, "Scanner"):
    Scanner = re.Scanner
else:
    import sre_parse
    import sre_compile
    class Scanner:
        def __init__(self, lexicon, flags=0):
            from sre_constants import BRANCH, SUBPATTERN
            self.lexicon = lexicon
            # combine phrases into a compound pattern
            p = []
            s = sre_parse.Pattern()
            s.flags = flags
            for phrase, action in lexicon:
                p.append(sre_parse.SubPattern(s, [
                    (SUBPATTERN, (len(p)+1, sre_parse.parse(phrase, flags))),
                    ]))
            s.groups = len(p)+1
            p = sre_parse.SubPattern(s, [(BRANCH, (None, p))])
            self.scanner = sre_compile.compile(p)
        def scan(self, string):
            result = []
            append = result.append
            match = self.scanner.scanner(string).match
            i = 0
            while 1:
                m = match()
                if not m:
                    break
                j = m.end()
                if i == j:
                    break
                action = self.lexicon[m.lastindex-1][1]
                if hasattr(action, '__call__'):
                    self.match = m
                    action = action(self, m.group())
                if action is not None:
                    append(action)
                i = j
            return result, string[i:]

# itertools.product available in Python 2.6+
import itertools
if modern_ok and hasattr(itertools, "product"):
    itertools_product = itertools.product
else:
    # Copied directly from the Python documentation:
    def itertools_product(*args, **kwds):
        # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
        # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
        pools = map(tuple, args) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x+[y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)    

# functools available in Python 2.5+
# This is just a cosmetic thing, so don't bother emulating it if we don't
# have it.
def compat_wraps(f1):
    def do_wrap(f2):
        return f2
    return do_wrap
if modern_ok:
    try:
        from functools import wraps
    except ImportError:
        wraps = compat_wraps
else:
    wraps = compat_wraps

# collections.Mapping available in Python 2.6+
import collections
if modern_ok and hasattr(collections, "Mapping"):
    Mapping = collections.Mapping
else:
    Mapping = dict
