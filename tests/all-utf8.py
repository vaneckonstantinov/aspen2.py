#!/usr/bin/env python
import sys

from six import unichr

for i in range(2**16):
    u = unichr(i).encode('utf8')
    sys.stdout.write("%5d %s  " % (i, u))
    if i % 6 == 0:
        print()

