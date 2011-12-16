Empirical credible interval
===========================

Given a sample from a distribution, construct the shortest interval
which includes x% of the samples.  This requires in the order of
1e6 samples for two digits of precision at the 95% interval.

Questions we want answered:

1. How many samples are required for 1-sigma intervals?  (about 1e5)

2. Is the answer returned from smaller draws biased? (yes)

3. Can we remove the bias? (we can reduce it, but the currrent
technique doesn't work for all distributions)

4. If we make certain assumptions about the underlying distribution
(e.g., smooth, unimodal, few inflection points) can we improve the
estimate beyond the points we happened to sample?  (not yet)

Manifest
========

explore.py

  Run calculation and produce plots for a variety of distributions
  on common intervals (1-sigma and 95%).  Run this one.

stats.py

  Calculates credible intervals.

bootstrap.py

  Attempt to improve the credible interval estimate for a small
  sample by bootstrapping it into a larger sample.
