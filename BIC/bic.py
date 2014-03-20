#!/usr/bin/env python
from __future__ import division, print_function
from numpy import *

def gen_problem(roots,n):
    p = poly1d(roots,True)
    x  = linspace(-2,2,n)
    y = p(x)
    dy = 1.0/(abs(x)+1)
    y += random.randn(*x.shape)*dy
    return x,y,dy

def perform_fit(problem,max_degree=3):
    x,y,dy = problem
    results = []
    for deg in range(max_degree+1):
        pp = polyfit(x,y,deg,w=dy**-2)
        SSE = sum((polyval(pp,x) - y)**2 * dy**-2)
        BIC = SSE + (deg+1)*log(len(y))
        #print("degree: %d  SSE: %.2f  BIC: %.2f"%(deg,SSE,BIC))
        results.append((BIC,SSE,pp))

    # Sort results by minimum BIC
    results = list(sorted(results))
    min_BIC,min_SSE,min_pp = results[0]
    #print("best BIC: %.1f for degree %d, SSE %.1f"
    #      %(min_BIC, len(min_pp)-1, min_SSE))

    # By Occam's razor, if a lower degree has SSE within 95% CI 
    # then we should choose it over the higher degree.
    # 95% CI for SSE => exp(-0.5*(SSE-min_SSE)) > 0.05 => SSE-min_SSE < ~6
    # Using delta BIC instead gives more power to even lower degrees
    # according the delta k ln n, where k is the #pars and n is the #points.
    # Using the test of BIC differences given in Kass & Raferty
    results = [(len(pp),BIC,SSE,pp) 
               for BIC,SSE,pp in results
               if BIC-min_BIC <= 6]
    results = list(sorted(results))
    degree, BIC, SSE, pp = results[0]
    #if len(pp) != len(min_pp):
    #    print("degree %d => %d"%(len(min_pp)-1,len(pp)-1))
    return pp,SSE
    #return min_pp,min_SSE

def run_analysis(roots, n):
    print("Roots:",roots,"#points:",n)
    max_degree = len(roots)*2+2
    nruns = 10000
    table = [[] for k in range(max_degree+1)]
    for _ in range(nruns):
        pp,SSE = perform_fit(gen_problem(roots,n),max_degree=max_degree) 
        table[len(pp)-1].append(SSE)

    for degree,SSEs in enumerate(table):
        if SSEs: 
            DOF = n - (degree+1)
            expected = "%.1f +/- %.1f"%(DOF, sqrt(2*DOF))
            actual = "%.1f +/- %.1f"%(mean(SSEs), std(SSEs))
            print("%2d: %5.1f%%  expected SSE: %s  actual SSEs: %s"
                  %(degree, 100*len(SSEs)/nruns, expected, actual)) 

random.seed(1)
run_analysis(roots=[-1,1,1.5], n=17)
