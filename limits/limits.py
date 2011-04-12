"""
Check interaction between limits and multiprocessing

Linux
=====

Test system:

  2.6.31-22-generic #73-Ubuntu SMP Fri Feb 11 19:18:05 UTC 2011 x86_64 GNU/Linux

CPU:

  SIGXCPU emitted every second between soft limit and hard limit

memory:

  no signal given

disk:

  SIGXFSZ emitted when file is too large, which raises
  IOError(27) File too large

Raising an error in the signal handler seem to work

"""

import time
import math

from multiprocessing import Process

from resource import setrlimit, RLIMIT_CPU, RLIMIT_FSIZE, RLIMIT_DATA
import signal
IGNORE = 'SIG_DFL', 'SIG_IGN', 'SIGKILL', 'SIGSTOP'
SIGTABLE = dict((v,k) for k,v in signal.__dict__.items()
                if k.startswith("SIG") and k not in IGNORE)

def sig_handler(signum, frame):
    name = SIGTABLE.get(signum,'UNKNOWN')
    print "received signal", name, signum
    raise RuntimeError("Resources exceeded")

def set_signals():
    for v,k in SIGTABLE.items():
        #print "setting signal",k,v
        signal.signal(v, sig_handler)

def stress_cpu(n):
    print "start time stress"
    t = time.time()
    while time.time() - t < n+10:
        for i in range(100000): math.exp(5)
    print "end time stress"
def stress_disk(n):
    print "start disk stress"
    fid = open("/tmp/stress_disk","w")
    block = 'z'*100000
    while n > len(block):
    	fid.write(block)
        n -= len(block)
    fid.write(block[:n])
    fid.close()
    print "end disk stress"
def stress_memory(n):
    print "start memory stress"
    z = 'z'*int(n)
    print len(z)
    print "end memory stress"

def test(resource, limit):
    set_signals()
    if resource == 'cpu':
        setrlimit(RLIMIT_CPU, (limit,2*limit))
        stress_cpu(2*limit+1)
    elif resource == 'disk':
        setrlimit(RLIMIT_FSIZE, (limit,2*limit))
        stress_disk(2*limit+1000000)
    elif resource == 'memory':
        setrlimit(RLIMIT_DATA, (limit,2*limit))
        stress_memory(2*limit+1000000)

def main():
    p = Process(target=test, args=('cpu',5))
    p.start()
    p.join()
    p = Process(target=test, args=('memory',1e8))
    p.start()
    p.join()
    p = Process(target=test, args=('disk',1e6))
    p.start()
    p.join()

if __name__ == "__main__": main()
