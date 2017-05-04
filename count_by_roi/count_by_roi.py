from __future__ import division, print_function

import numpy as np
from numpy import random
from matplotlib import pyplot as plt
from scipy.stats import gaussian_kde

def simulate(monitor_rate=1000., detector_rate=1., cutoff_time=300, cutoff_counts=100, cycles=10000, correction=0.):
    beta = 1./detector_rate
    results = []
    for k in range(cycles):
        arrival_times = np.cumsum(random.exponential(scale=beta, size=cutoff_counts))
        if arrival_times[-1] >= cutoff_time:
            detector_counts = np.searchsorted(arrival_times, cutoff_time) + correction
            count_time = cutoff_time
        else:
            detector_counts = cutoff_counts
            count_time = arrival_times[-1]
        monitor_counts = random.poisson(monitor_rate*count_time)+1
        counts_per_second = detector_counts / count_time
        counts_per_monitor = detector_counts / (monitor_counts + (monitor_counts == 0))
        #if k < 100: print("%2d %.1f %.3f"%(detector_counts, count_time, counts_per_second))
        results.append((counts_per_second, counts_per_monitor))
    counts_per_second, counts_per_monitor = [np.array(v) for v in zip(*results)]

    expected_counts = min(detector_rate*cutoff_time, cutoff_counts)
    expected_time = min(cutoff_time, cutoff_counts/detector_rate)
    expected_monitor = monitor_rate*expected_time
    expected_counts_per_second = expected_counts / expected_time
    expected_counts_per_second_error = np.sqrt(expected_counts)/expected_time
    expected_counts_per_monitor, expected_counts_per_monitor_variance = \
        div_err(expected_counts, expected_counts, expected_monitor, expected_monitor)
    expected_counts_per_monitor_error = np.sqrt(expected_counts_per_monitor_variance)

    if expected_counts < 100:
        lim = int(np.ceil(np.sqrt(expected_counts)))
        bins = np.arange(-3*lim, 4*lim) + expected_counts
        cps_bins = bins/expected_time
        cpm_bins = bins/expected_monitor
    else:
        lim = 3.5
        bins = np.linspace(-lim, lim, 51)
        cps_bins = bins*expected_counts_per_second_error + expected_counts_per_second
        cpm_bins = bins*expected_counts_per_monitor_error + expected_counts_per_monitor
    cps, cps_kde = kde(counts_per_second, cps_bins)
    cpm, cpm_kde = kde(counts_per_monitor, cpm_bins)

    plt.clf()
    plt.subplot(121)
    #plt.hist(counts_per_second, normed=True, bins=cps_bins)
    #plt.hist(np.round(nbins/detector_rate*counts_per_second)*detector_rate/nbins, bins=nbins+1, normed=True)
    plt.plot(cps, cps_kde)
    plt.axvline(expected_counts_per_second, c='r')
    plt.xlabel("rate (per second)")
    plt.ylabel("Probability of being observed")
    plt.subplot(122)
    #plt.hist(counts_per_monitor, normed=True, bins=cpm_bins)
    #plt.hist(np.round(nbins*monitor_rate/detector_rate*counts_per_second)*detector_rate/monitor_rate/nbins, bins=nbins+1, normed=True)
    plt.plot(cpm, cpm_kde)
    plt.axvline(expected_counts_per_monitor, c='r')
    plt.xlabel("rate (per monitor)")
    plt.suptitle("""\
 detector: %g/s;   monitor: %g/s;  max: %g counts or %g s
 expected %g counts in %g seconds"""
 % (detector_rate, monitor_rate, cutoff_counts, cutoff_time,
    expected_counts, expected_time))


def kde(points, bins):
    mu, sigma = np.mean(points), np.std(points)
    kde = gaussian_kde((points-mu)/sigma)
    x = np.linspace(bins[0], bins[-1], 400)
    p = kde((x-mu)/sigma)
    return x, p

def div_err(X, varX, Y, varY):
    """Division with error propagation"""
    # Direct algorithm:
    #   Z = X/Y
    #   varZ = (varX/X**2 + varY/Y**2) * Z**2
    #        = (varX + varY * Z**2) / Y**2
    # Indirect algorithm to minimize intermediates
    #np.seterr(all='raise')
    Z = X/Y      # truediv => Z is a float
    varZ = Z**2  # Z is a float => varZ is a float
    varZ *= varY
    varZ += varX
    # Z/Y/Y is more expensive than Z/Y**2 (poor data locality going through
    # the Y array twice), but it avoids creating a temporary for Y**2.
    # Also, happens to avoid integer overflow on Y**2...
    varZ /= Y
    varZ /= Y
    return Z, varZ