#!/usr/bin/env python
"""
Demonstration that mean and std can estimate the histogram shape from a
normal distribution.
"""
from pylab import *

n = 1000
mu = 2
sigma = 0.3

# fake data
s = randn(n)*sigma + mu

# estimates
mu_hat, sigma_hat = mean(s), std(s)

# plot
t = linspace(mu-3*sigma,mu+3*sigma,200)
bins = linspace(t[0],t[-1],21)
step = bins[1]-bins[0]
def G(x,m,s): return exp(-((x-m)/s)**2/2)/sqrt(2*pi*s**2)
hist(s,bins=bins)
plot(t,G(t,mu_hat,sigma_hat)*n*step,'g',hold=True)
show()
