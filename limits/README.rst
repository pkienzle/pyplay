Question
========

How do I impose cpu/disk/memory limits on processes?

Test
====

run the following::

    python limits.py


Linux
=====

Test system::

  2.6.31-22-generic #73-Ubuntu SMP Fri Feb 11 19:18:05 UTC 2011 x86_64 GNU/Linux

CPU:

  SIGXCPU emitted every second between soft limit and hard limit

memory:

  no signal given

disk:

  SIGXFSZ emitted when file is too large, which raises
  IOError(27) File too large

Raising an error in the signal handler seem to work

