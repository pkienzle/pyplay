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

Mac OS 10.4
===========

Test system::

  8.11.1 Darwin Kernel Version 8.11.1: Wed Oct 10 18:23:28 PDT 2007; root:xnu-792.25.20~1/RELEASE_I386 i386 i386

Behaviour as in above linux system, but SIGXCPU emitted every 1/10th of
a second or so.
   
