Paul Kienzle 2013-12-05

Question
========

Do we need poisson statistics for fitting peaks in low backgrounds, or can
we get away with a some sort of corrected normal approximation?

Test
====

The program `<testdy>`_ runs through peak fitting trials using a simulated
gaussian peak in low background.  For each simulation, the data were
fitted using poisson statistics, and for gaussian statistics with various
estimates of y,dy for each fit.  The proposed correction comes from:

  `<http://www-cdf.fnal.gov/physics/statistics/notes/pois_eb.txt>`_

The conditions were:

* correction: y=n+1/2, dy=sqrt(n+1/4) for n <=N.
* conventional: y=n, dy=sqrt(n+(n==0))
* poisson: use the poisson cost function, not a gaussian approximation

3 point peaks in a 30 point scan of differing background level, 300 trials 
for each background level.

Conclusions
===========

Using the Poisson cost function, the original parameters were recovered 
pretty reliably.  The normal approximation is only reliable for n greater 
than about 7.  The n+1/2 correction doesn't compensate for the bias.

Pretty clearly, if you care about background levels for low background 
counts, you should be using poisson stats for your fits.  This will not 
affect peak position or peak width. Peak amplitude and background level 
will clearly trade off each other.

I didn't bother playing with misshapen peaks --- if your model is broken, 
all bets are off for the fit.

Results
=======

1) 20% zeros shows a definite underestimation of background levels, even 
with the correction.  

Command: $ ./testdy 100,0.4,0.1,1

===========  ============ ============ ============ ============ ===========
condition    A            mu           sigma        C            chisq        
===========  ============ ============ ============ ============ ===========
target       100.0        0.4          0.1          1.0                       
conventional 100.0(48)    0.4005(42)   0.0988(31)   0.68(20)     21.8(61)     
correct0     100.3(48)    0.4005(43)   0.0984(32)   0.64(12)     21.4(69)     
correct1     100.1(48)    0.4005(43)   0.0985(32)   0.73(16)     22.4(69)     
correct2     100.0(48)    0.4005(43)   0.0986(32)   0.75(18)     23.5(69)     
correctall   100.2(48)    0.4005(43)   0.0995(33)   0.75(18)     24.9(73)     
poisson      99.7(47)     0.4004(40)   0.1004(30)   0.98(28)     24.6(78)     
===========  ============ ============ ============ ============ ===========


2) fewer than 20% <= 2

Command: $ ./testdy 100,0.4,0.1,4

===========  ============ ============ ============ ============ ===========
condition    A            mu           sigma        C            chisq        
===========  ============ ============ ============ ============ ===========
target       100.0        0.4          0.1          4.0                       
conventional 100.3(47)    0.4001(42)   0.1003(40)   2.87(63)     28.2(80)     
correct0     100.3(48)    0.4001(42)   0.1006(43)   2.72(79)     29.5(96)     
correct1     100.3(48)    0.4001(42)   0.1004(42)   2.86(77)     27.8(95)     
correct2     100.2(48)    0.4001(42)   0.1002(42)   2.98(79)     27.0(98)     
correctall   100.3(48)    0.4001(42)   0.1007(44)   3.23(90)     29(11)       
poisson      100.1(47)    0.4002(40)   0.1001(38)   3.90(58)     35(12)       
===========  ============ ============ ============ ============ ===========

3) mostly n > 7

Command: $ ./testdy 100,0.4,0.1,10

===========  ============ ============ ============ ============ ===========
condition    A            mu           sigma        C            chisq        
===========  ============ ============ ============ ============ ===========
target       100.0        0.4          0.1          10.0                      
conventional 100.3(53)    0.4000(45)   0.0997(45)   9.1(11)      27.7(88)     
correct0     100.3(53)    0.4000(45)   0.0997(45)   9.1(11)      27.7(88)     
correct1     100.3(53)    0.4000(45)   0.0997(45)   9.1(11)      27.7(86)     
correct2     100.3(53)    0.4000(45)   0.0997(45)   9.1(10)      27.6(85)     
correctall   100.3(53)    0.4000(45)   0.0997(45)   9.6(10)      27.1(84)     
poisson      100.2(51)    0.3999(45)   0.0995(42)   10.09(90)    30(11)       
===========  ============ ============ ============ ============ ===========

