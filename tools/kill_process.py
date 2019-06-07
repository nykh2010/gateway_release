#!/usr/bin/env python3
import os
import sys

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(1)
    cmd = "ps | grep %s | grep -v 'grep' | awk '{print $1}'" % (sys.argv[1])
    with os.popen(cmd) as fp:
        pids = fp.readlines()
    for pid in pids:
        os.system("kill -9 {}".format(pid))
    sys.exit(0)