#__docformat__ = "restructuredtext en"
# ******NOTICE***************
# optimize.py module by Travis E. Oliphant
#
# You may copy and use this module as you see fit with no
# guarantee implied provided you keep this notice in all copies.
# *****END NOTICE************

# A collection of optimization algorithms.  Version 0.5
# CHANGES
#  Added fminbound (July 2001)
#  Added brute (Aug. 2002)
#  Finished line search satisfying strong Wolfe conditions (Mar. 2004)
#  Updated strong Wolfe conditions line search to use cubic-interpolation (Mar. 2004)

# PAK: removed algs that depend on line_search

# Minimization routines

__all__ = ['fmin', 'fmin_powell',
           'fminbound','brent', 'golden','bracket','rosen','rosen_der',
           'rosen_hess', 'rosen_hess_prod', 'brute', 'approx_fprime',
           'check_grad']

__docformat__ = "restructuredtext en"

import numpy
from numpy import atleast_1d, eye, mgrid, argmin, zeros, shape, \
     squeeze, vectorize, asarray, absolute, sqrt, Inf, asfarray, isinf

# These have been copied from Numeric's MLab.py
# I don't think they made the transition to scipy_core
def max(m,axis=0):
    """max(m,axis=0) returns the maximum of m along dimension axis.
    """
    m = asarray(m)
    return numpy.maximum.reduce(m,axis)

def min(m,axis=0):
    """min(m,axis=0) returns the minimum of m along dimension axis.
    """
    m = asarray(m)
    return numpy.minimum.reduce(m,axis)

def is_array_scalar(x):
    """Test whether `x` is either a scalar or an array scalar.

    """
    return len(atleast_1d(x) == 1)

abs = absolute
import __builtin__
pymin = __builtin__.min
pymax = __builtin__.max
__version__="0.7"
_epsilon = sqrt(numpy.finfo(float).eps)

def vecnorm(x, ord=2):
    if ord == Inf:
        return numpy.amax(abs(x))
    elif ord == -Inf:
        return numpy.amin(abs(x))
    else:
        return numpy.sum(abs(x)**ord,axis=0)**(1.0/ord)

def rosen(x):
    """The Rosenbrock function.

    The function computed is

        sum(100.0*(x[1:] - x[:-1]**2.0)**2.0 + (1 - x[:-1])**2.0

    Parameters
    ----------
    x : array_like, 1D
        The point at which the Rosenbrock function is to be computed.

    Returns
    -------
    f : float
        The value of the Rosenbrock function

    See Also
    --------
    rosen_der, rosen_hess, rosen_hess_prod
    """
    x = asarray(x)
    return numpy.sum(100.0*(x[1:]-x[:-1]**2.0)**2.0 + (1-x[:-1])**2.0,axis=0)

def rosen_der(x):
    """The derivative (i.e. gradient) of the Rosenbrock function.

    Parameters
    ----------
    x : array_like, 1D
        The point at which the derivative is to be computed.

    Returns
    -------
    der : 1D numpy array
        The gradient of the Rosenbrock function at `x`.

    See Also
    --------
    rosen, rosen_hess, rosen_hess_prod
    """
    x = asarray(x)
    xm = x[1:-1]
    xm_m1 = x[:-2]
    xm_p1 = x[2:]
    der = numpy.zeros_like(x)
    der[1:-1] = 200*(xm-xm_m1**2) - 400*(xm_p1 - xm**2)*xm - 2*(1-xm)
    der[0] = -400*x[0]*(x[1]-x[0]**2) - 2*(1-x[0])
    der[-1] = 200*(x[-1]-x[-2]**2)
    return der

def rosen_hess(x):
    """The Hessian matrix of the Rosenbrock function.

    Parameters
    ----------
    x : array_like, 1D
        The point at which the Hessian matrix is to be computed.

    Returns
    -------
    hess : 2D numpy array
        The Hessian matrix of the Rosenbrock function at `x`.

    See Also
    --------
    rosen, rosen_der, rosen_hess_prod
    """
    x = atleast_1d(x)
    H = numpy.diag(-400*x[:-1],1) - numpy.diag(400*x[:-1],-1)
    diagonal = numpy.zeros(len(x), dtype=x.dtype)
    diagonal[0] = 1200*x[0]**2 - 400*x[1] + 2
    diagonal[-1] = 200
    diagonal[1:-1] = 202 + 1200*x[1:-1]**2 - 400*x[2:]
    H = H + numpy.diag(diagonal)
    return H

def rosen_hess_prod(x,p):
    """Product of the Hessian matrix of the Rosenbrock function with a vector.

    Parameters
    ----------
    x : array_like, 1D
        The point at which the Hessian matrix is to be computed.
    p : array_like, 1D, same size as `x`.
        The vector to be multiplied by the Hessian matrix.

    Returns
    -------
    v : 1D numpy array
        The Hessian matrix of the Rosenbrock function at `x` multiplied
        by the vector `p`.

    See Also
    --------
    rosen, rosen_der, rosen_hess
    """
    x = atleast_1d(x)
    Hp = numpy.zeros(len(x), dtype=x.dtype)
    Hp[0] = (1200*x[0]**2 - 400*x[1] + 2)*p[0] - 400*x[0]*p[1]
    Hp[1:-1] = -400*x[:-2]*p[:-2]+(202+1200*x[1:-1]**2-400*x[2:])*p[1:-1] \
               -400*x[1:-1]*p[2:]
    Hp[-1] = -400*x[-2]*p[-2] + 200*p[-1]
    return Hp

def wrap_function(function, args):
    ncalls = [0]
    def function_wrapper(x):
        ncalls[0] += 1
        return function(x, *args)
    return ncalls, function_wrapper

def fmin(func, x0, args=(), xtol=1e-4, ftol=1e-4, maxiter=None, maxfun=None,
         full_output=0, disp=1, retall=0, callback=None):
    """
    Minimize a function using the downhill simplex algorithm.

    Parameters
    ----------
    func : callable func(x,*args)
        The objective function to be minimized.
    x0 : ndarray
        Initial guess.
    args : tuple
        Extra arguments passed to func, i.e. ``f(x,*args)``.
    callback : callable
        Called after each iteration, as callback(xk), where xk is the
        current parameter vector.

    Returns
    -------
    xopt : ndarray
        Parameter that minimizes function.
    fopt : float
        Value of function at minimum: ``fopt = func(xopt)``.
    iter : int
        Number of iterations performed.
    funcalls : int
        Number of function calls made.
    warnflag : int
        1 : Maximum number of function evaluations made.
        2 : Maximum number of iterations reached.
    allvecs : list
        Solution at each iteration.

    Other parameters
    ----------------
    xtol : float
        Relative error in xopt acceptable for convergence.
    ftol : number
        Relative error in func(xopt) acceptable for convergence.
    maxiter : int
        Maximum number of iterations to perform.
    maxfun : number
        Maximum number of function evaluations to make.
    full_output : bool
        Set to True if fopt and warnflag outputs are desired.
    disp : bool
        Set to True to print convergence messages.
    retall : bool
        Set to True to return list of solutions at each iteration.

    Notes
    -----
    Uses a Nelder-Mead simplex algorithm to find the minimum of function of
    one or more variables.

    """
    fcalls, func = wrap_function(func, args)
    x0 = asfarray(x0).flatten()
    N = len(x0)
    rank = len(x0.shape)
    if not -1 < rank < 2:
        raise ValueError("Initial guess must be a scalar or rank-1 sequence.")
    if maxiter is None:
        maxiter = N * 200
    if maxfun is None:
        maxfun = N * 200

    rho = 1; chi = 2; psi = 0.5; sigma = 0.5;
    one2np1 = range(1,N+1)

    if rank == 0:
        sim = numpy.zeros((N+1,), dtype=x0.dtype)
    else:
        sim = numpy.zeros((N+1,N), dtype=x0.dtype)
    fsim = numpy.zeros((N+1,), float)
    sim[0] = x0
    if retall:
        allvecs = [sim[0]]
    fsim[0] = func(x0)
    nonzdelt = 0.05
    zdelt = 0.00025
    for k in range(0,N):
        y = numpy.array(x0,copy=True)
        if y[k] != 0:
            y[k] = (1+nonzdelt)*y[k]
        else:
            y[k] = zdelt

        sim[k+1] = y
        f = func(y)
        fsim[k+1] = f

    ind = numpy.argsort(fsim)
    fsim = numpy.take(fsim,ind,0)
    # sort so sim[0,:] has the lowest function value
    sim = numpy.take(sim,ind,0)

    iterations = 1

    while (fcalls[0] < maxfun and iterations < maxiter):
        if (max(numpy.ravel(abs(sim[1:]-sim[0]))) <= xtol \
            and max(abs(fsim[0]-fsim[1:])) <= ftol):
            break

        xbar = numpy.add.reduce(sim[:-1],0) / N
        xr = (1+rho)*xbar - rho*sim[-1]
        fxr = func(xr)
        doshrink = 0

        if fxr < fsim[0]:
            xe = (1+rho*chi)*xbar - rho*chi*sim[-1]
            fxe = func(xe)

            if fxe < fxr:
                sim[-1] = xe
                fsim[-1] = fxe
            else:
                sim[-1] = xr
                fsim[-1] = fxr
        else: # fsim[0] <= fxr
            if fxr < fsim[-2]:
                sim[-1] = xr
                fsim[-1] = fxr
            else: # fxr >= fsim[-2]
                # Perform contraction
                if fxr < fsim[-1]:
                    xc = (1+psi*rho)*xbar - psi*rho*sim[-1]
                    fxc = func(xc)

                    if fxc <= fxr:
                        sim[-1] = xc
                        fsim[-1] = fxc
                    else:
                        doshrink=1
                else:
                    # Perform an inside contraction
                    xcc = (1-psi)*xbar + psi*sim[-1]
                    fxcc = func(xcc)

                    if fxcc < fsim[-1]:
                        sim[-1] = xcc
                        fsim[-1] = fxcc
                    else:
                        doshrink = 1

                if doshrink:
                    for j in one2np1:
                        sim[j] = sim[0] + sigma*(sim[j] - sim[0])
                        fsim[j] = func(sim[j])

        ind = numpy.argsort(fsim)
        sim = numpy.take(sim,ind,0)
        fsim = numpy.take(fsim,ind,0)
        if callback is not None:
            callback(sim[0])
        iterations += 1
        if retall:
            allvecs.append(sim[0])

    x = sim[0]
    fval = min(fsim)
    warnflag = 0

    if fcalls[0] >= maxfun:
        warnflag = 1
        if disp:
            print "Warning: Maximum number of function evaluations has "\
                  "been exceeded."
    elif iterations >= maxiter:
        warnflag = 2
        if disp:
            print "Warning: Maximum number of iterations has been exceeded"
    else:
        if disp:
            print "Optimization terminated successfully."
            print "         Current function value: %f" % fval
            print "         Iterations: %d" % iterations
            print "         Function evaluations: %d" % fcalls[0]


    if full_output:
        retlist = x, fval, iterations, fcalls[0], warnflag
        if retall:
            retlist += (allvecs,)
    else:
        retlist = x
        if retall:
            retlist = (x, allvecs)

    return retlist


def approx_fprime(xk,f,epsilon,*args):
    f0 = f(*((xk,)+args))
    grad = numpy.zeros((len(xk),), float)
    ei = numpy.zeros((len(xk),), float)
    for k in range(len(xk)):
        ei[k] = epsilon
        grad[k] = (f(*((xk+ei,)+args)) - f0)/epsilon
        ei[k] = 0.0
    return grad

def check_grad(func, grad, x0, *args):
    return sqrt(sum((grad(x0,*args)-approx_fprime(x0,func,_epsilon,*args))**2))

def approx_fhess_p(x0,p,fprime,epsilon,*args):
    f2 = fprime(*((x0+epsilon*p,)+args))
    f1 = fprime(*((x0,)+args))
    return (f2 - f1)/epsilon


def fminbound(func, x1, x2, args=(), xtol=1e-5, maxfun=500,
              full_output=0, disp=1):
    """Bounded minimization for scalar functions.

    Parameters
    ----------
    func : callable f(x,*args)
        Objective function to be minimized (must accept and return scalars).
    x1, x2 : float or array scalar
        The optimization bounds.
    args : tuple
        Extra arguments passed to function.
    xtol : float
        The convergence tolerance.
    maxfun : int
        Maximum number of function evaluations allowed.
    full_output : bool
        If True, return optional outputs.
    disp : int
        If non-zero, print messages.
            0 : no message printing.
            1 : non-convergence notification messages only.
            2 : print a message on convergence too.
            3 : print iteration results.


    Returns
    -------
    xopt : ndarray
        Parameters (over given interval) which minimize the
        objective function.
    fval : number
        The function value at the minimum point.
    ierr : int
        An error flag (0 if converged, 1 if maximum number of
        function calls reached).
    numfunc : int
      The number of function calls made.

    Notes
    -----
    Finds a local minimizer of the scalar function `func` in the
    interval x1 < xopt < x2 using Brent's method.  (See `brent`
    for auto-bracketing).

    """
    # Test bounds are of correct form

    if not (is_array_scalar(x1) and is_array_scalar(x2)):
        raise ValueError("Optimisation bounds must be scalars"
                         " or array scalars.")
    if x1 > x2:
        raise ValueError("The lower bound exceeds the upper bound.")

    flag = 0
    header = ' Func-count     x          f(x)          Procedure'
    step='       initial'

    sqrt_eps = sqrt(2.2e-16)
    golden_mean = 0.5*(3.0-sqrt(5.0))
    a, b = x1, x2
    fulc = a + golden_mean*(b-a)
    nfc, xf = fulc, fulc
    rat = e = 0.0
    x = xf
    fx = func(x,*args)
    num = 1
    fmin_data = (1, xf, fx)

    ffulc = fnfc = fx
    xm = 0.5*(a+b)
    tol1 = sqrt_eps*abs(xf) + xtol / 3.0
    tol2 = 2.0*tol1

    if disp > 2:
        print (" ")
        print (header)
        print "%5.0f   %12.6g %12.6g %s" % (fmin_data + (step,))


    while ( abs(xf-xm) > (tol2 - 0.5*(b-a)) ):
        golden = 1
        # Check for parabolic fit
        if abs(e) > tol1:
            golden = 0
            r = (xf-nfc)*(fx-ffulc)
            q = (xf-fulc)*(fx-fnfc)
            p = (xf-fulc)*q - (xf-nfc)*r
            q = 2.0*(q-r)
            if q > 0.0: p = -p
            q = abs(q)
            r = e
            e = rat

            # Check for acceptability of parabola
            if ( (abs(p) < abs(0.5*q*r)) and (p > q*(a-xf)) and \
                 (p < q*(b-xf))):
                rat = (p+0.0) / q;
                x = xf + rat
                step = '       parabolic'

                if ((x-a) < tol2) or ((b-x) < tol2):
                    si = numpy.sign(xm-xf) + ((xm-xf)==0)
                    rat = tol1*si
            else:      # do a golden section step
                golden = 1

        if golden:  # Do a golden-section step
            if xf >= xm:
                e=a-xf
            else:
                e=b-xf
            rat = golden_mean*e
            step = '       golden'

        si = numpy.sign(rat) + (rat == 0)
        x = xf + si*max([abs(rat), tol1])
        fu = func(x,*args)
        num += 1
        fmin_data = (num, x, fu)
        if disp > 2:
            print "%5.0f   %12.6g %12.6g %s" % (fmin_data + (step,))

        if fu <= fx:
            if x >= xf:
                a = xf
            else:
                b = xf
            fulc, ffulc = nfc, fnfc
            nfc, fnfc = xf, fx
            xf, fx = x, fu
        else:
            if x < xf:
                a = x
            else:
                b = x
            if (fu <= fnfc) or (nfc == xf):
                fulc, ffulc = nfc, fnfc
                nfc, fnfc = x, fu
            elif (fu <= ffulc) or (fulc == xf) or (fulc == nfc):
                fulc, ffulc = x, fu

        xm = 0.5*(a+b)
        tol1 = sqrt_eps*abs(xf) + xtol/3.0
        tol2 = 2.0*tol1

        if num >= maxfun:
            flag = 1
            fval = fx
            if disp > 0:
                _endprint(x, flag, fval, maxfun, xtol, disp)
            if full_output:
                return xf, fval, flag, num
            else:
                return xf

    fval = fx
    if disp > 0:
        _endprint(x, flag, fval, maxfun, xtol, disp)

    if full_output:
        return xf, fval, flag, num
    else:
        return xf

class Brent:
    #need to rethink design of __init__
    def __init__(self, func, args=(), tol=1.48e-8, maxiter=500,
                 full_output=0):
        self.func = func
        self.args = args
        self.tol = tol
        self.maxiter = maxiter
        self._mintol = 1.0e-11
        self._cg = 0.3819660
        self.xmin = None
        self.fval = None
        self.iter = 0
        self.funcalls = 0

    #need to rethink design of set_bracket (new options, etc)
    def set_bracket(self, brack = None):
        self.brack = brack
    def get_bracket_info(self):
        #set up
        func = self.func
        args = self.args
        brack = self.brack
        ### BEGIN core bracket_info code ###
        ### carefully DOCUMENT any CHANGES in core ##
        if brack is None:
            xa,xb,xc,fa,fb,fc,funcalls = bracket(func, args=args)
        elif len(brack) == 2:
            xa,xb,xc,fa,fb,fc,funcalls = bracket(func, xa=brack[0],
                                                 xb=brack[1], args=args)
        elif len(brack) == 3:
            xa,xb,xc = brack
            if (xa > xc):  # swap so xa < xc can be assumed
                dum = xa; xa=xc; xc=dum
            assert ((xa < xb) and (xb < xc)), "Not a bracketing interval."
            fa = func(*((xa,)+args))
            fb = func(*((xb,)+args))
            fc = func(*((xc,)+args))
            assert ((fb<fa) and (fb < fc)), "Not a bracketing interval."
            funcalls = 3
        else:
            raise ValueError("Bracketing interval must be " \
                             "length 2 or 3 sequence.")
        ### END core bracket_info code ###

        return xa,xb,xc,fa,fb,fc,funcalls

    def optimize(self):
        #set up for optimization
        func = self.func
        xa,xb,xc,fa,fb,fc,funcalls = self.get_bracket_info()
        _mintol = self._mintol
        _cg = self._cg
        #################################
        #BEGIN CORE ALGORITHM
        #we are making NO CHANGES in this
        #################################
        x=w=v=xb
        fw=fv=fx=func(*((x,)+self.args))
        if (xa < xc):
            a = xa; b = xc
        else:
            a = xc; b = xa
        deltax= 0.0
        funcalls = 1
        iter = 0
        while (iter < self.maxiter):
            tol1 = self.tol*abs(x) + _mintol
            tol2 = 2.0*tol1
            xmid = 0.5*(a+b)
            if abs(x-xmid) < (tol2-0.5*(b-a)):  # check for convergence
                xmin=x; fval=fx
                break
            if (abs(deltax) <= tol1):
                if (x>=xmid): deltax=a-x       # do a golden section step
                else: deltax=b-x
                rat = _cg*deltax
            else:                              # do a parabolic step
                tmp1 = (x-w)*(fx-fv)
                tmp2 = (x-v)*(fx-fw)
                p = (x-v)*tmp2 - (x-w)*tmp1;
                tmp2 = 2.0*(tmp2-tmp1)
                if (tmp2 > 0.0): p = -p
                tmp2 = abs(tmp2)
                dx_temp = deltax
                deltax= rat
                # check parabolic fit
                if ((p > tmp2*(a-x)) and (p < tmp2*(b-x)) and (abs(p) < abs(0.5*tmp2*dx_temp))):
                    rat = p*1.0/tmp2        # if parabolic step is useful.
                    u = x + rat
                    if ((u-a) < tol2 or (b-u) < tol2):
                        if xmid-x >= 0: rat = tol1
                        else: rat = -tol1
                else:
                    if (x>=xmid): deltax=a-x # if it's not do a golden section step
                    else: deltax=b-x
                    rat = _cg*deltax

            if (abs(rat) < tol1):            # update by at least tol1
                if rat >= 0: u = x + tol1
                else: u = x - tol1
            else:
                u = x + rat
            fu = func(*((u,)+self.args))      # calculate new output value
            funcalls += 1

            if (fu > fx):                 # if it's bigger than current
                if (u<x): a=u
                else: b=u
                if (fu<=fw) or (w==x):
                    v=w; w=u; fv=fw; fw=fu
                elif (fu<=fv) or (v==x) or (v==w):
                    v=u; fv=fu
            else:
                if (u >= x): a = x
                else: b = x
                v=w; w=x; x=u
                fv=fw; fw=fx; fx=fu

            iter += 1
        #################################
        #END CORE ALGORITHM
        #################################

        self.xmin = x
        self.fval = fx
        self.iter = iter
        self.funcalls = funcalls

    def get_result(self, full_output=False):
        if full_output:
            return self.xmin, self.fval, self.iter, self.funcalls
        else:
            return self.xmin


def brent(func, args=(), brack=None, tol=1.48e-8, full_output=0, maxiter=500):
    """Given a function of one-variable and a possible bracketing interval,
    return the minimum of the function isolated to a fractional precision of
    tol.

    Parameters
    ----------
    func : callable f(x,*args)
        Objective function.
    args
        Additional arguments (if present).
    brack : tuple
        Triple (a,b,c) where (a<b<c) and func(b) <
        func(a),func(c).  If bracket consists of two numbers (a,c)
        then they are assumed to be a starting interval for a
        downhill bracket search (see `bracket`); it doesn't always
        mean that the obtained solution will satisfy a<=x<=c.
    full_output : bool
        If True, return all output args (xmin, fval, iter,
        funcalls).

    Returns
    -------
    xmin : ndarray
        Optimum point.
    fval : float
        Optimum value.
    iter : int
        Number of iterations.
    funcalls : int
        Number of objective function evaluations made.

    Notes
    -----
    Uses inverse parabolic interpolation when possible to speed up
    convergence of golden section method.

    """

    brent = Brent(func=func, args=args, tol=tol,
                  full_output=full_output, maxiter=maxiter)
    brent.set_bracket(brack)
    brent.optimize()
    return brent.get_result(full_output=full_output)


def golden(func, args=(), brack=None, tol=_epsilon, full_output=0):
    """ Given a function of one-variable and a possible bracketing interval,
    return the minimum of the function isolated to a fractional precision of
    tol.

    Parameters
    ----------
    func : callable func(x,*args)
        Objective function to minimize.
    args : tuple
        Additional arguments (if present), passed to func.
    brack : tuple
        Triple (a,b,c), where (a<b<c) and func(b) <
        func(a),func(c).  If bracket consists of two numbers (a,
        c), then they are assumed to be a starting interval for a
        downhill bracket search (see `bracket`); it doesn't always
        mean that obtained solution will satisfy a<=x<=c.
    tol : float
        x tolerance stop criterion
    full_output : bool
        If True, return optional outputs.

    Notes
    -----
    Uses analog of bisection method to decrease the bracketed
    interval.

    """
    if brack is None:
        xa,xb,xc,fa,fb,fc,funcalls = bracket(func, args=args)
    elif len(brack) == 2:
        xa,xb,xc,fa,fb,fc,funcalls = bracket(func, xa=brack[0], xb=brack[1], args=args)
    elif len(brack) == 3:
        xa,xb,xc = brack
        if (xa > xc):  # swap so xa < xc can be assumed
            dum = xa; xa=xc; xc=dum
        assert ((xa < xb) and (xb < xc)), "Not a bracketing interval."
        fa = func(*((xa,)+args))
        fb = func(*((xb,)+args))
        fc = func(*((xc,)+args))
        assert ((fb<fa) and (fb < fc)), "Not a bracketing interval."
        funcalls = 3
    else:
        raise ValueError("Bracketing interval must be length 2 or 3 sequence.")

    _gR = 0.61803399
    _gC = 1.0-_gR
    x3 = xc
    x0 = xa
    if (abs(xc-xb) > abs(xb-xa)):
        x1 = xb
        x2 = xb + _gC*(xc-xb)
    else:
        x2 = xb
        x1 = xb - _gC*(xb-xa)
    f1 = func(*((x1,)+args))
    f2 = func(*((x2,)+args))
    funcalls += 2
    while (abs(x3-x0) > tol*(abs(x1)+abs(x2))):
        if (f2 < f1):
            x0 = x1; x1 = x2; x2 = _gR*x1 + _gC*x3
            f1 = f2; f2 = func(*((x2,)+args))
        else:
            x3 = x2; x2 = x1; x1 = _gR*x2 + _gC*x0
            f2 = f1; f1 = func(*((x1,)+args))
        funcalls += 1
    if (f1 < f2):
        xmin = x1
        fval = f1
    else:
        xmin = x2
        fval = f2
    if full_output:
        return xmin, fval, funcalls
    else:
        return xmin


def bracket(func, xa=0.0, xb=1.0, args=(), grow_limit=110.0, maxiter=1000):
    """Given a function and distinct initial points, search in the
    downhill direction (as defined by the initital points) and return
    new points xa, xb, xc that bracket the minimum of the function
    f(xa) > f(xb) < f(xc). It doesn't always mean that obtained
    solution will satisfy xa<=x<=xb

    Parameters
    ----------
    func : callable f(x,*args)
        Objective function to minimize.
    xa, xb : float
        Bracketing interval.
    args : tuple
        Additional arguments (if present), passed to `func`.
    grow_limit : float
        Maximum grow limit.
    maxiter : int
        Maximum number of iterations to perform.

    Returns
    -------
    xa, xb, xc : float
        Bracket.
    fa, fb, fc : float
        Objective function values in bracket.
    funcalls : int
        Number of function evaluations made.

    """
    _gold = 1.618034
    _verysmall_num = 1e-21
    fa = func(*(xa,)+args)
    fb = func(*(xb,)+args)
    if (fa < fb):                      # Switch so fa > fb
        dum = xa; xa = xb; xb = dum
        dum = fa; fa = fb; fb = dum
    xc = xb + _gold*(xb-xa)
    fc = func(*((xc,)+args))
    funcalls = 3
    iter = 0
    while (fc < fb):
        tmp1 = (xb - xa)*(fb-fc)
        tmp2 = (xb - xc)*(fb-fa)
        val = tmp2-tmp1
        if abs(val) < _verysmall_num:
            denom = 2.0*_verysmall_num
        else:
            denom = 2.0*val
        w = xb - ((xb-xc)*tmp2-(xb-xa)*tmp1)/denom
        wlim = xb + grow_limit*(xc-xb)
        if iter > maxiter:
            raise RuntimeError("Too many iterations.")
        iter += 1
        if (w-xc)*(xb-w) > 0.0:
            fw = func(*((w,)+args))
            funcalls += 1
            if (fw < fc):
                xa = xb; xb=w; fa=fb; fb=fw
                return xa, xb, xc, fa, fb, fc, funcalls
            elif (fw > fb):
                xc = w; fc=fw
                return xa, xb, xc, fa, fb, fc, funcalls
            w = xc + _gold*(xc-xb)
            fw = func(*((w,)+args))
            funcalls += 1
        elif (w-wlim)*(wlim-xc) >= 0.0:
            w = wlim
            fw = func(*((w,)+args))
            funcalls += 1
        elif (w-wlim)*(xc-w) > 0.0:
            fw = func(*((w,)+args))
            funcalls += 1
            if (fw < fc):
                xb=xc; xc=w; w=xc+_gold*(xc-xb)
                fb=fc; fc=fw; fw=func(*((w,)+args))
                funcalls += 1
        else:
            w = xc + _gold*(xc-xb)
            fw = func(*((w,)+args))
            funcalls += 1
        xa=xb; xb=xc; xc=w
        fa=fb; fb=fc; fc=fw
    return xa, xb, xc, fa, fb, fc, funcalls



def _linesearch_powell(func, p, xi, tol=1e-3):
    """Line-search algorithm using fminbound.

    Find the minimium of the function ``func(x0+ alpha*direc)``.

    """
    def myfunc(alpha):
        return func(p + alpha * xi)
    alpha_min, fret, iter, num = brent(myfunc, full_output=1, tol=tol)
    xi = alpha_min*xi
    return squeeze(fret), p+xi, xi


def fmin_powell(func, x0, args=(), xtol=1e-4, ftol=1e-4, maxiter=None,
                maxfun=None, full_output=0, disp=1, retall=0, callback=None,
                direc=None):
    """
    Minimize a function using modified Powell's method.

    Parameters
    ----------
    func : callable f(x,*args)
        Objective function to be minimized.
    x0 : ndarray
        Initial guess.
    args : tuple
        Extra arguments passed to func.
    callback : callable
        An optional user-supplied function, called after each
        iteration.  Called as ``callback(xk)``, where ``xk`` is the
        current parameter vector.
    direc : ndarray
        Initial direction set.

    Returns
    -------
    xopt : ndarray
        Parameter which minimizes `func`.
    fopt : number
        Value of function at minimum: ``fopt = func(xopt)``.
    direc : ndarray
        Current direction set.
    iter : int
        Number of iterations.
    funcalls : int
        Number of function calls made.
    warnflag : int
        Integer warning flag:
            1 : Maximum number of function evaluations.
            2 : Maximum number of iterations.
    allvecs : list
        List of solutions at each iteration.

    Other Parameters
    ----------------
    xtol : float
        Line-search error tolerance.
    ftol : float
        Relative error in ``func(xopt)`` acceptable for convergence.
    maxiter : int
        Maximum number of iterations to perform.
    maxfun : int
        Maximum number of function evaluations to make.
    full_output : bool
        If True, fopt, xi, direc, iter, funcalls, and
        warnflag are returned.
    disp : bool
        If True, print convergence messages.
    retall : bool
        If True, return a list of the solution at each iteration.

    Notes
    -----
    Uses a modification of Powell's method to find the minimum of
    a function of N variables.

    """
    # we need to use a mutable object here that we can update in the
    # wrapper function
    fcalls, func = wrap_function(func, args)
    x = asarray(x0).flatten()
    if retall:
        allvecs = [x]
    N = len(x)
    rank = len(x.shape)
    if not -1 < rank < 2:
        raise ValueError("Initial guess must be a scalar or rank-1 sequence.")
    if maxiter is None:
        maxiter = N * 1000
    if maxfun is None:
        maxfun = N * 1000


    if direc is None:
        direc = eye(N, dtype=float)
    else:
        direc = asarray(direc, dtype=float)

    fval = squeeze(func(x))
    x1 = x.copy()
    iter = 0;
    ilist = range(N)
    while True:
        fx = fval
        bigind = 0
        delta = 0.0
        for i in ilist:
            direc1 = direc[i]
            fx2 = fval
            fval, x, direc1 = _linesearch_powell(func, x, direc1, tol=xtol*100)
            if (fx2 - fval) > delta:
                delta = fx2 - fval
                bigind = i
        iter += 1
        if callback is not None:
            callback(x)
        if retall:
            allvecs.append(x)
        if (2.0*(fx - fval) <= ftol*(abs(fx)+abs(fval))+1e-20): break
        if fcalls[0] >= maxfun: break
        if iter >= maxiter: break

        # Construct the extrapolated point
        direc1 = x - x1
        x2 = 2*x - x1
        x1 = x.copy()
        fx2 = squeeze(func(x2))

        if (fx > fx2):
            t = 2.0*(fx+fx2-2.0*fval)
            temp = (fx-fval-delta)
            t *= temp*temp
            temp = fx-fx2
            t -= delta*temp*temp
            if t < 0.0:
                fval, x, direc1 = _linesearch_powell(func, x, direc1,
                                                     tol=xtol*100)
                direc[bigind] = direc[-1]
                direc[-1] = direc1

    warnflag = 0
    if fcalls[0] >= maxfun:
        warnflag = 1
        if disp:
            print "Warning: Maximum number of function evaluations has "\
                  "been exceeded."
    elif iter >= maxiter:
        warnflag = 2
        if disp:
            print "Warning: Maximum number of iterations has been exceeded"
    else:
        if disp:
            print "Optimization terminated successfully."
            print "         Current function value: %f" % fval
            print "         Iterations: %d" % iter
            print "         Function evaluations: %d" % fcalls[0]

    x = squeeze(x)

    if full_output:
        retlist = x, fval, direc, iter, fcalls[0], warnflag
        if retall:
            retlist += (allvecs,)
    else:
        retlist = x
        if retall:
            retlist = (x, allvecs)

    return retlist




def _endprint(x, flag, fval, maxfun, xtol, disp):
    if flag == 0:
        if disp > 1:
            print "\nOptimization terminated successfully;\n" \
                  "The returned value satisfies the termination criteria\n" \
                  "(using xtol = ", xtol, ")"
    if flag == 1:
        print "\nMaximum number of function evaluations exceeded --- " \
              "increase maxfun argument.\n"
    return


def brute(func, ranges, args=(), Ns=20, full_output=0, finish=fmin):
    """Minimize a function over a given range by brute force.

    Parameters
    ----------
    func : callable ``f(x,*args)``
        Objective function to be minimized.
    ranges : tuple
        Each element is a tuple of parameters or a slice object to
        be handed to ``numpy.mgrid``.
    args : tuple
        Extra arguments passed to function.
    Ns : int
        Default number of samples, if those are not provided.
    full_output : bool
        If True, return the evaluation grid.

    Returns
    -------
    x0 : ndarray
        Value of arguments to `func`, giving minimum over the grid.
    fval : int
        Function value at minimum.
    grid : tuple
        Representation of the evaluation grid.  It has the same
        length as x0.
    Jout : ndarray
        Function values over grid:  ``Jout = func(*grid)``.

    Notes
    -----
    Find the minimum of a function evaluated on a grid given by
    the tuple ranges.

    """
    N = len(ranges)
    if N > 40:
        raise ValueError("Brute Force not possible with more " \
              "than 40 variables.")
    lrange = list(ranges)
    for k in range(N):
        if type(lrange[k]) is not type(slice(None)):
            if len(lrange[k]) < 3:
                lrange[k] = tuple(lrange[k]) + (complex(Ns),)
            lrange[k] = slice(*lrange[k])
    if (N==1):
        lrange = lrange[0]

    def _scalarfunc(*params):
        params = squeeze(asarray(params))
        return func(params,*args)

    vecfunc = vectorize(_scalarfunc)
    grid = mgrid[lrange]
    if (N==1):
        grid = (grid,)
    Jout = vecfunc(*grid)
    Nshape = shape(Jout)
    indx = argmin(Jout.ravel(),axis=-1)
    Nindx = zeros(N,int)
    xmin = zeros(N,float)
    for k in range(N-1,-1,-1):
        thisN = Nshape[k]
        Nindx[k] = indx % Nshape[k]
        indx = indx // thisN
    for k in range(N):
        xmin[k] = grid[k][tuple(Nindx)]

    Jmin = Jout[tuple(Nindx)]
    if (N==1):
        grid = grid[0]
        xmin = xmin[0]
    if callable(finish):
        vals = finish(func,xmin,args=args,full_output=1, disp=0)
        xmin = vals[0]
        Jmin = vals[1]
        if vals[-1] > 0:
            print "Warning: Final optimization did not succeed"
    if full_output:
        return xmin, Jmin, grid, Jout
    else:
        return xmin


def main():
    import time

    times = []
    algor = []
    x0 = [0.8,1.2,0.7]
    print "Nelder-Mead Simplex"
    print "==================="
    start = time.time()
    x = fmin(rosen,x0)
    print x
    times.append(time.time() - start)
    algor.append('Nelder-Mead Simplex\t')

    print
    print "Powell Direction Set Method"
    print "==========================="
    start = time.time()
    x = fmin_powell(rosen,x0)
    print x
    times.append(time.time() - start)
    algor.append('Powell Direction Set Method.')

    print
    print "Nonlinear CG"
    print "============"
    start = time.time()
    x = fmin_cg(rosen, x0, fprime=rosen_der, maxiter=200)
    print x
    times.append(time.time() - start)
    algor.append('Nonlinear CG     \t')

    print
    print "BFGS Quasi-Newton"
    print "================="
    start = time.time()
    x = fmin_bfgs(rosen, x0, fprime=rosen_der, maxiter=80)
    print x
    times.append(time.time() - start)
    algor.append('BFGS Quasi-Newton\t')

    print
    print "BFGS approximate gradient"
    print "========================="
    start = time.time()
    x = fmin_bfgs(rosen, x0, gtol=1e-4, maxiter=100)
    print x
    times.append(time.time() - start)
    algor.append('BFGS without gradient\t')


    print
    print "Newton-CG with Hessian product"
    print "=============================="
    start = time.time()
    x = fmin_ncg(rosen, x0, rosen_der, fhess_p=rosen_hess_prod, maxiter=80)
    print x
    times.append(time.time() - start)
    algor.append('Newton-CG with hessian product')


    print
    print "Newton-CG with full Hessian"
    print "==========================="
    start = time.time()
    x = fmin_ncg(rosen, x0, rosen_der, fhess=rosen_hess, maxiter=80)
    print x
    times.append(time.time() - start)
    algor.append('Newton-CG with full hessian')

    print
    print "\nMinimizing the Rosenbrock function of order 3\n"
    print " Algorithm \t\t\t       Seconds"
    print "===========\t\t\t      ========="
    for k in range(len(algor)):
        print algor[k], "\t -- ", times[k]

if __name__ == "__main__":
    main()
