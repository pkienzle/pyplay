Question
========

Can BIC recover the order of a polynomial model used to generate a dataset?

Does the distribution of $\chi^2$ for the resulting fit match the expected
value $k$ degrees of freedom, with uncertainty $\sqrt{2 k}$?

Test
====

Run the following::

    python bic.py

Modify bic.py for different polynomial roots, different number of data points,
and (in perform_fit) the choice of best BIC or minimum degree best BIC.

Results
=======

Using the lowest BIC value, averaging over 10000 runs::

 Roots: [-1, 1, 1.5] #points: 171
 3:  95.7%  expected SSE: 167.0 +/- 18.3  actual SSEs: 167.0 +/- 18.4
 4:   3.8%  expected SSE: 166.0 +/- 18.2  actual SSEs: 164.4 +/- 17.7
 5:   0.4%  expected SSE: 165.0 +/- 18.2  actual SSEs: 167.1 +/- 15.7
 6:   0.1%  expected SSE: 164.0 +/- 18.1  actual SSEs: 176.7 +/- 24.2
 7:   0.0%  expected SSE: 163.0 +/- 18.1  actual SSEs: 159.7 +/- 14.3

 Roots: [-1, 1, 1.5] #points: 17
 3:  84.0%  expected SSE: 13.0 +/- 5.1  actual SSEs: 12.4 +/- 4.7
 4:   9.8%  expected SSE: 12.0 +/- 4.9  actual SSEs: 11.4 +/- 4.7
 5:   3.5%  expected SSE: 11.0 +/- 4.7  actual SSEs: 10.6 +/- 4.6
 6:   1.6%  expected SSE: 10.0 +/- 4.5  actual SSEs: 9.4 +/- 3.7
 7:   0.8%  expected SSE: 9.0 +/- 4.2  actual SSEs: 8.8 +/- 3.5
 8:   0.4%  expected SSE: 8.0 +/- 4.0  actual SSEs: 7.6 +/- 3.3

Using the lowest degree whose BIC is within 6 of the best BIC::

 Roots: [-1, 1, 1.5] #points: 171
 3:  99.7%  expected SSE: 167.0 +/- 18.3  actual SSEs: 167.2 +/- 18.4
 4:   0.3%  expected SSE: 166.0 +/- 18.2  actual SSEs: 160.9 +/- 14.5
 6:   0.0%  expected SSE: 164.0 +/- 18.1  actual SSEs: 193.9 +/- 0.0

 Roots: [-1, 1, 1.5] #points: 17
 3:  98.6%  expected SSE: 13.0 +/- 5.1  actual SSEs: 13.2 +/- 5.1
 4:   0.9%  expected SSE: 12.0 +/- 4.9  actual SSEs: 13.9 +/- 5.4
 5:   0.3%  expected SSE: 11.0 +/- 4.7  actual SSEs: 12.6 +/- 5.1
 6:   0.1%  expected SSE: 10.0 +/- 4.5  actual SSEs: 8.0 +/- 3.9
 7:   0.1%  expected SSE: 9.0 +/- 4.2  actual SSEs: 12.1 +/- 4.3
 8:   0.0%  expected SSE: 8.0 +/- 4.0  actual SSEs: 3.9 +/- 0.0

Conclusions
===========

The raw BIC test does a pretty good job of finding the correct model
order, especially if there are enough data points to identify the model
well, but is worthwhile to consider those models with (BIC-BIC\ :sub:`min`)<6.
By Occam's Razor, those models with fewer parameters which fit almost as well
should be preferred.
