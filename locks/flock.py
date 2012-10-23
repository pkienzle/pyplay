#!/usr/bin/env python

import sys
import fcntl
import traceback

def main():
    if len(sys.argv) < 2:
        print 'usage: ./flock.py journal entry details...'
        sys.exit(1)
    with open("journal","a") as fid:
      #for i in range(2):               # append: multiple rounds
        raw_input("opened and ready to lock > ");
        print "locking..."
        fcntl.flock(fid,fcntl.LOCK_EX)
        #fid.seek(0,2)
        fid.write(" ".join(sys.argv[1:])+"\n")
        raw_input("locked and waiting > ");
        #fid.flush()                    # append: flush before releasing
        #fcntl.flock(fid,fcntl.LOCK_UN) # append: release before next round
    raw_input("closed > ");

if __name__ == "__main__": main()
