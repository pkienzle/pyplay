from __future__ import division, print_function

import numpy as np
from numpy import random
from matplotlib import pyplot as plt
from scipy.stats import gaussian_kde

def simulate(monitor_rate=1000., detector_rate=1., cutoff_time=300, cutoff_counts=100, 
             cycles=10000, correction=0., show_pure=False):
    #time_cor, roi_cor = correction, 1. # correct fixed time: add part of a count to detector
    time_cor, roi_cor = 0., (1+correction/cutoff_counts) # correct fixed counts: add part of an interval to the time
    beta = 1./detector_rate
    results = []
    for k in range(cycles):
        arrival_times = np.cumsum(random.exponential(scale=beta, size=cutoff_counts))
        if arrival_times[-1] >= cutoff_time:
            # Stop at cutoff time, so count by time
            detector_counts = np.searchsorted(arrival_times, cutoff_time) + time_cor 
            count_time = cutoff_time
        else:
            # Stop before cutoff time, so count by ROI
            detector_counts = cutoff_counts/roi_cor
            count_time = arrival_times[-1]
        monitor_counts = random.poisson(monitor_rate*count_time)+0.5
        counts_per_second = detector_counts / count_time
        counts_per_monitor = detector_counts / (monitor_counts + (monitor_counts == 0))
        # Save the rate if ROI was used without a cutoff time.
        pure_roi = cutoff_counts/roi_cor / arrival_times[-1]
        #if k < 100: print("%2d %.1f %.3f"%(detector_counts, count_time, counts_per_second))
        results.append((counts_per_second, counts_per_monitor, pure_roi))
    counts_per_second, counts_per_monitor, pure_roi = [np.array(v) for v in zip(*results)]

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

    text1 = ("expected cps: %.3f +/- %.3f\nmean cps: %0.3f"
             %(expected_counts_per_second, expected_counts_per_second_error, np.mean(counts_per_second)))
    cps, cps_kde = kde(counts_per_second, cps_bins)
    cpm, cpm_kde = kde(counts_per_monitor, cpm_bins)

    plt.clf()
    plt.subplot(121)
    #plt.hist(counts_per_second, normed=True, bins=cps_bins)
    #plt.hist(np.round(nbins/detector_rate*counts_per_second)*detector_rate/nbins, bins=nbins+1, normed=True)
    plt.plot(cps, cps_kde, label='joint')
    plt.axvline(expected_counts_per_second, c='k')
    plt.xlabel("rate (per second)")
    plt.ylabel("Probability of being observed")

    if show_pure:
        # Use poisson generator for the pure time distribution.  This is a bit
        # of a cheat since it doesn't use the same sequence of events for all
        # three statistics, however it is somewhat more difficult to do pure
        # time from the event sequence since you don't know how many events
        # are required to exceed the cutoff time.
        pure_time = (random.poisson(detector_rate*cutoff_time, size=cycles)+time_cor)/cutoff_time
        text2 = ("mean cps (counts): %0.3f\nmean cps (time): %0.3f"%(np.mean(pure_roi), np.mean(pure_time)))
        _, roi_kde = kde(pure_roi, cps_bins)
        _, time_kde = kde(pure_time, cps_bins)
        plt.plot(cps, roi_kde, label='fixed counts')
        plt.plot(cps, time_kde, label='fixed time')
        plt.legend()
        plt.text(0.05, 0.95, "\n".join((text1, text2)), va='top', transform=plt.gca().transAxes)
    else:
        plt.text(0.05, 0.95, text1, va='top', transform=plt.gca().transAxes)
    plt.subplot(122)
    #plt.hist(counts_per_monitor, normed=True, bins=cpm_bins)
    #plt.hist(np.round(nbins*monitor_rate/detector_rate*counts_per_second)*detector_rate/monitor_rate/nbins, bins=nbins+1, normed=True)
    if show_pure:
        plt.plot((cps-expected_counts_per_second)/expected_counts_per_second_error, cps_kde)
        plt.xlabel("normalized (rate-expected)/expected_err")
        plt.grid(True)
    else:
        plt.plot(cpm, cpm_kde)
        plt.axvline(expected_counts_per_monitor, c='k')
        plt.xlabel("rate (per monitor)")
    plt.suptitle("""\
 detector: %g/s;   monitor: %g/s;  max: %g counts or %g s
 expected %g counts in %g seconds"""
 % (detector_rate, monitor_rate, cutoff_counts, cutoff_time,
    expected_counts, expected_time))


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

def scipy_stats_density(points, bins):
    mu, sigma = np.mean(points), np.std(points)
    kde = gaussian_kde((points-mu)/sigma)
    x = np.linspace(bins[0], bins[-1], 400)
    p = kde((x-mu)/sigma)/sigma
    return x, p


def sklearn_density(sample_points, evaluation_points):
    """
    Estimate the probability density function from which a set of sample
    points was drawn and return the estimated density at the evaluation points.
    """
    from sklearn.neighbors import KernelDensity

    x = np.linspace(evaluation_points[0], evaluation_points[-1], 400)
    sample_points = sample_points[:, None]
    evaluation_points = x[:, None]

    # Silverman bandwidth estimator
    n, d = sample_points.shape
    bandwidth = (n * (d + 2) / 4.)**(-1. / (d + 4))

    # Standardize data so that we can use uniform bandwidth.
    # Note that we will need to scale the resulting density by sigma to
    # correct the area.
    mu, sigma = np.mean(sample_points, axis=0), np.std(sample_points, axis=0)
    data, points = (sample_points - mu)/sigma, (evaluation_points - mu)/sigma

    #print("starting grid search for bandwidth over %d points"%n)
    #from sklearn.grid_search import GridSearchCV
    #from numpy import logspace
    #params = {'bandwidth': logspace(-1, 1, 20)}
    #fitter = GridSearchCV(KernelDensity(), params)
    #fitter.fit(data)
    #kde = fitter.best_estimator_
    #print("best bandwidth: {0}".format(kde.bandwidth))
    #import time; T0 = time.time()
    kde = KernelDensity(kernel='gaussian', bandwidth=bandwidth,
                        rtol=1e-6, atol=1e-6)
    #print("T:%6.3f   fitting"%(time.time()-T0))
    kde.fit(data)
    #print("T:%6.3f   estimating"%(time.time()-T0))
    log_pdf = kde.score_samples(points)
    #print("T:%6.3f   done"%(time.time()-T0))
    return x, np.exp(log_pdf)/np.prod(sigma)  # undo the x scaling on the data points

#kde = scipy_stats_density
kde = sklearn_density
