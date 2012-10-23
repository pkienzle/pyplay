Paul Kienzle 2012-10-23

Question
========

Study the behaviour of linux locks, in particular to see if the
lock is released when a process is killed with SIG_KILL.

Test
====

There are four locking programs all with the same logic:

* flock.py uses the fcntl.flock call to lock the whole file
* lock.py uses fcntl.lockf, which calls fcntl to lock byte 0
* lock.c uses fcntl to lock byte 0
* lock.java uses the getChannel().lock(), which locks byte 0

I don't know how to trigger flock() from Java, and didn't bother
to try it from C.  Build the C and java by typing "make" on the
command line.

The checking process is a bit involved, and will require two
consoles T1 and T2::

    T1-in  $ ./lock.py line one
    T1-in  opened > <enter>
    T1-out locking...
    T1-out locked >

    T2-in  $ ./lock.py line two
    T2-in  opened > <enter>
    T2-out locking...

    T1-in  locked > <enter>
    T1-in  closed > <enter>
    T1-out $

    T2-out locked >
    T2-in  locked > <enter>
    T2-in  closed > <enter>
    T2-out $

If you now look at the journal file in the same directory, it
should contain::

    line one
    line two

So the basic locking works.  Now you can repeat the test using
different kill scenarios on T1 including Ctrl-C, kill and kill -9,
and using different runtime environments (C, python, java).  

The C program can be run using::

    $ ./lock [msg ...]

and the java program can be run using::

    $ java lock

The message defaults to "<lang> write" if not given on the command
line.  The java program does not accept command line arguments.

I did have some concern about a race condition between opening
and locking, which would allow the first process to move to the
current end of the file, the second process to extend the file,
and the first file to overwrite the second since the file cursor
is not updated.  Testing on linux, this was not the case.
Apparently, the POSIX standard says that if the file is opened 
for append then there is an implicit seek(0,2) before each write.

Conclusions
===========

# Use flock rather than lockf in python if you want to interact 
  with java locks.

# To keep a journal file in python use::

    import fnctl
    with open("journal","a") as fid:
        fnctl.lockf(fid,fnctl.LOCK_EX)
        fid.write("entry\n")

  On exiting the "with" context, the file is flushed and the
  lock is released.  

# Java is a little more involved::

    import java.io.File;
    import java.io.IOException;
    import java.io.FileOutputStream;

    public class lock {
      public static void main(String[] args) throws IOException {
        File filename = new File("journal");
        FileOutputStream handle = new FileOutputStream(filename, true);
        handle.getChannel().lock();
        handle.write("entry\n".getBytes());
        handle.close();
      }
    }

# C uses::

    #include <stdlib.h>
    #include <unistd.h>
    #include <stdio.h>
    #include <fcntl.h>
    #include <string.h>

    int main(int argc, char *argv[])
    {
       int fd = open("journal", O_WRONLY|O_CREAT|O_APPEND);

       struct flock lock;
       lock.l_type = F_WRLCK;
       lock.l_whence = SEEK_SET;
       lock.l_start = 0;
       lock.l_len = 0;
       lock.l_pid = 0;

       if (fcntl(fd, F_SETLKW, &lock) == -1) { 
          printf("could not obtain lock\n");
          exit(1);
       }

       write(fd, "entry\n", 6);
       close(fd);
       exit(0);
    }


Notes
=====

More sophisticated uses of the journal which keep it open 
rather than relying on close would need more steps.  In 
particular, you should make sure that the current process  
flushes the writes and frees the lock when it is busy elsewhere.

Something like the following could be used in a python
worker process::

    fid = open("journal","a")

    while not work.empty():
        next_work = work.get()
        try:
            fnctl.lockf(fid, fnctl.LOCK_EX) 
            fid.write(next_work.description)
            fid.flush()
        finally:
            fnctl.lockf(fid, fnctl.LOCK_UN)
        next_work.run()

    fid.close()

Reopening the file each time would be a little simpler, but check 
that this doesn't impact the performance too badly::

    while not work.empty():
        next_work = work.get()
        with open("journal","a") as fid:
            fnctl.lockf(fid, fnctl.LOCK_EX)
            fid.write(next_work.description)
        next_work.run()

