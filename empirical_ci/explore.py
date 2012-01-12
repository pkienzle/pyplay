import pylab
from numpy import random, logspace, log10, sqrt, mean, std, diff, array
from stats import credible_interval as ci
from scipy.special import erf

def cauchy(x=0,gamma=1,size=None):
    return random.standard_cauchy(size=size)*gamma+x

low_points = 15    # 10-1000
mid_points = 5    # 1e3-1e5
high_points = 3    # 1e5-1e7
work = int(1e6)  # maximum work gathering stats
maxn = 100      # max number of draws for a given k
dists = {
  'normal': lambda n: random.randn(int(n))*3.5  + 10,  # width 7
  'gamma':  lambda n: random.gamma(2,2,size=int(n)), # asymmetric
  'cauchy': lambda n: cauchy(-2,1,size=int(n)), # long tails and asymmetric
}
intervals = {
  '1-sigma': erf(1/sqrt(2)),
  '95%': 0.95,
  }

z = [int(ki) for ki in logspace(1,3,low_points)]
if mid_points: z += [int(ki) for ki in logspace(3,5,mid_points)]
if high_points: z += [int(ki) for ki in logspace(5,7,high_points)]
z = list(sorted(set(z))) # Make z unique

ni,nj = len(intervals),len(dists)
for pi,interval_name  in enumerate(sorted(intervals.keys())):
    for pj,dist_name in enumerate(sorted(dists.keys())):
        print "processing",dist_name,interval_name
        s,rng = intervals[interval_name], dists[dist_name]
        #print [min(1000,work//ki+1) for ki in z]
        unbiased = [array([ci(rng(ki),s,unbiased=True) 
                           for _ in range(min(maxn,work//ki+1))])
                    for ki in z]
        biased = [array([ci(rng(ki),s,unbiased=False) 
                         for _ in range(min(maxn,work//ki+1))])
                  for ki in z]
        pylab.subplot(ni,nj,pi*nj+pj+1)
        #print data
        for data in biased, unbiased:
            delta = [diff(di,axis=1)[:,0] for di in data]
            w = [mean(di) for di in delta]
            dw = [std(di) for di in delta]
        #print z,w,dw
        #print interval_name, dist_name, ni, nj, pi, pj, pj*ni+pi
            pylab.semilogx(z,w,'o')
            pylab.errorbar(z,w,dw)
            if pj == 0: pylab.ylabel(interval_name)
            if pi == 0: pylab.title(dist_name)
        #label='dist: %s\ninterval: %s'%(dist_name,interval_name)
        #pylab.text(0,0,label,ha="left",va="bottom",
        #           transform=pylab.gca().transAxes)
print "Done..."
pylab.show()
