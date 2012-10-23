#!/usr/bin/env python

import sys
import fcntl
import traceback
import struct

def main():
    msg = " ".join(sys.argv[1:]) if len(sys.argv)>1 else "python write"
    with open("journal","a") as fid:
      #for i in range(2):               # multiple rounds
        raw_input("opened > ");
        print "locking..."
        fcntl.lockf(fid, fcntl.LOCK_EX)
        #fid.seek(0,2)
        fid.write(msg+"\n")
        raw_input("locked > ");
        #fid.flush()                            # flush before releasing
        #fcntl.lockf(fid, fcntl.LOCK_UN)
    raw_input("closed > ");

if __name__ == "__main__": main()
