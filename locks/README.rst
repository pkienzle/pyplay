Question
========

Study the behaviour of linux locks, in particular to see if the
lock is released when a process is killed with SIG_KILL.

Test
====

The checking process is a bit involved, and will require two
consoles T1 and T2::

    T1-in  $ ./flock.py line one
    T1-out opened and ready to lock >
    T1-in  opened and ready to lock > <enter>
    T1-out locking...
    T1-out locked and waiting >

    T2-in  $ ./flock.py line two
    T2-out opened and ready to lock >
    T2-in  opened and ready to lock > <enter>
    T2-out locking...

    T1-in  locked and waiting > <enter>
    T1-out $

    T2-out locked and waiting >
    T2-in  locked and waiting > <enter>
    T2-out $

If you now look at the journal file in the same directory, it
should contain::

    line one
    line two

So the basic locking works.  Now you can repeat the test using
different kill scenarios on T1 including Ctrl-C, kill and kill -9.

I did have some concern about a race condition between opening
and locking, which would allow the first process to move to the
current end of the file, the second process to extend the file,
and the first file to overwrite the second since the file cursor
is not updated.  Testing on linux, this was not the case.
Apparently, the POSIX standard says that if the file is opened 
for append then there is an implicit seek(0,2) before each write.

Conclusion
==========

To keep a journal file::

    import fnctl
    # open the file for append
    with open("journal","a") as fid:
        fnctl.flock(fid,fnctl.LOCK_EX)
        fid.write("entry\n")

On exiting the "with" context, the file is flushed and the
lock is released.  

More sophisticated uses of the journal which keep it open 
rather than relying on close would need more steps.  In 
particular, you should make sure that the current process  
flushes the writes and frees the lock when it is busy elsewhere.

Something like the following could be used in a worker process::

    fid = open("journal","a")

    while not work.empty():
        next_work = work.get()
        try:
            fnctl.flock(fid, fnctl.LOCK_EX) 
            fid.write(next_work.description)
            fid.flush()
        finally:
            fnctl.flock(fid, fnctl.LOCK_UN)
        next_work.run()

    fid.close()

Reopening the file each time would be a little simpler, but check 
that this doesn't impact the performance too badly::

    while not work.empty():
        next_work = work.get()
        with open("journal","a") as fid:
            fnctl.flock(fid, fnctl.LOCK_EX)
            fid.write(next_work.description)
        next_work.run()

