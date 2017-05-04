Count by Region of Interest
===========================

A bit of a surprise,  you have to be careful when interpreting data
with both time and ROI cutoff as stopping conditions for a counting
experiment.

When performing neutron scattering experiments the primary observable is the
count rate for the given experimental condition.  The rate is estimated by
counting the scattered neturons for a certain amount of time and dividing by
the counting time. Since the incident neutron beam is assumed to be generated
by a `Poisson process <https://en.wikipedia.org/wiki/Poisson_distribution>`_,
the variance in the number of counts for a given count rate is equal to the
number of counts, and relative uncertainty in the counts goes down
as sqrt(N). The uncertainty in the rate is sqrt(N)/T for counting time T. To
make best use of available beam time, we therefore would like to count until
we reach a given statistical uncertainty and then stop, either because
sqrt(N)/N is small at large N or because sqrt(N)/T is small at large T.
That is, we want to stop counting at a fixed T cutoff or a fixed N cutoff.

To simulate the experiment I generated N neutron arrival intervals from the
exponential distribution, where N was the cutoff count value.  A cumulative
sum on the intervals gives the arrival time of the kth neutron.  If the
total time was greater than the cutoff time, then the experiment recorded the
number of events before the cutoff time over the cutoff time.  If the
total time was less than the cutoff time, then the experiment recorded
N over the total time.

A further note, since the neutron source is not necessarily constant
flux, we maintain a monitor in the beam to estimate the total incident
flux rather than strictly relying on time.  The monitor rates are assumed
to be large enough that monitor uncertainty is small relative to count
uncertainty.  The expected monitor counts for the experiment was the
experiment time multiplied by the cutoff time.  The observed monitors for
the experiment was then drawn from a Poisson distribution with this value.

I ran some simulations where the detector rate favoured count limited
measurements and some where the measurements were time limited.  The left
graph normalizes by time and the right by monitor. The red bar shows the
true count rate.  As you can see, the true count rate is about in the
center of the distribution of observed count rates.

.. image:: count_limited.png
    :alt: Plot of observed count rates when counts is the cutoff
    :align: left

.. image:: time_limited.png
    :alt: Plot of observed count rates when time is the cutoff
    :align: left

Where things get tricky is when the count rate is such that cutoff counts
is approximately equal to the cutoff time so sometimes the time is
reached and sometimes the counts are reached. This leads to the double peak
in the next figure for time-and-count limited measurements.  It is very
reproducible, and is not an artifact of binning or the size of n.

.. image:: time_or_count_limited.png
    :alt: Plot of observed count rates for matched counts and time
    :align: left

You can compensate for this by shifting the rate peak slightly for the count
by time case by adding 0.5 to the estimated counts for the interval.

.. image:: time_or_count_with_correction.png
    :alt: Plot of observed count rates for matched condition with correction
    :align: left

This issue is that the distribution of rates estimated from counts
by time vs counts by ROI are different, and they lead to problems
at the crossover, where some counts are limited by rate and others
are limited by time.  You can see an exaggerated example of this
in the final figure, where it is clear that the shape is different
and the peak is shifted.

.. image:: time_vs_count_rates.png
    :alt: Plot of observed count rates given a fixed time vs fixed counts cutoff
    :align: left

This is not quite the correct problem.  We are showing the probability of
observed rate given a fixed true rate.  Rather than plotting observed rates
for a give true rate, we should be plotting the true rate for given observed
rate.  This is a little harder to do, and is a project for another day.

Requiring adding 0.5 to all observed counts by time (the usual case) in order
to make this artifact disappear is not acceptable without further analysis.

Code used to produce the plots::

    n = 100
    cycles = 100000
    # expected count cutoff
    count_by_roi.simulate(cutoff_counts=n, cycles=cycles, detector_rate=n/100.)
    # expected time cutoff
    count_by_roi.simulate(cutoff_counts=n, cycles=cycles, detector_rate=n/600.)
    # count or time cutoff
    count_by_roi.simulate(cutoff_counts=n, cycles=cycles, detector_rate=n/300.)
    # count or time cutoff with correction
    count_by_roi.simulate(cutoff_counts=n, cycles=cycles, detector_rate=n/300., correction=0.5)

Code showing observed rate distribution when counting a given rate
by time and by count::

    subplot(121)
    plt.hist(10./np.sum(np.random.exponential(0.1, size=(10,10000)), axis=0), bins=arange(0.5,30.5,1.))
    title("rate from 10 counts at 10/s"); ylabel("freq"); xlabel("rate (1/s)")
    subplot(122)
    plt.hist(np.random.poisson(10, size=10000), bins=arange(0.5,30.5,1.))
    title("rate from 1 s at 10/s"); ylabel("freq"); xlabel("rate (1/s)")

    # And maybe overplot the "corrected" rate distribution
    subplot(121)
    plt.hist(10.5/np.sum(np.random.exponential(0.1, size=(10,10000)), axis=0), bins=arange(0.5,30.5,1.))

Manifest
========

count_by_roi.py

    Program used to run the simulations

count_limited.png, time_limited.png, time_or_count_limited.png

    Results from running code without correction in the three conditions

time_or_count_with_correction.png

    Results from running code with correction

time_vs_count_rates.png

    Comparison of probability of individual count rates being observed
    for a true count rate of 10/s.