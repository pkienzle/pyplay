# Attempt to bootstrap an unbiased shortest credible interval
# from a sparse sample by sampling from the empirical cdf modeled 
# as a linear spline.  The answer appears to be the same as the
# ci computed directly.
from numpy.random import rand
from numpy import sort, hstack, arange, searchsorted, diff
import stats
def bootstrap_ci(v, ci, n):
    v = sort(v)
    v = hstack( (v[0]-abs(v[0]), v, v[-1]+abs(v[-1])) )
    dv = diff(v)
    cdf = arange(v.size-1,dtype='d')/(v.size-2)
    #print cdf
    idx = searchsorted(cdf,rand(n))
    #print idx
    x = v[idx]+dv[idx]*rand(n)
    return stats.credible_interval(x,ci)
    
