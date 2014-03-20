from __future__ import division
import time
import numpy
from mpi4py import MPI
comm = MPI.COMM_WORLD

MPITYPE = {
    numpy.dtype('int8'):MPI.SIGNED_CHAR,
    numpy.dtype('int16'):MPI.SHORT,
    numpy.dtype('int32'):MPI.INT,
    numpy.dtype('int64'):MPI.LONG,
    numpy.dtype('float32'):MPI.FLOAT,
    numpy.dtype('float64'):MPI.DOUBLE,
    }


def mpimap(f, a, root=0, inplace=False):
    # Share array dimensions with slaves
    array_info = (a.size,a.dtype) if comm.rank == root else None
    n,dtype = comm.bcast(array_info, root=root)
    mpitype = MPITYPE[dtype]
    #print "array",n,dtype

    # Build whole
    whole = numpy.ascontiguousarray(a, dtype=dtype) if comm.rank==root else None

    # Build parts
    idx = numpy.arange(comm.size)
    size = numpy.ones(comm.size,idx.dtype)*(n//comm.size) + (idx<n%comm.size)
    offset = numpy.cumsum(numpy.hstack((0,size[:-1])))
    part = numpy.empty(size[comm.rank], dtype=dtype)

    #if comm.rank==root: print "whole",whole,list(zip(offset,size))

    # Distribute
    comm.Scatterv((whole,(size,offset),mpitype), (part,mpitype), root=root)
    #print "part",comm.rank, part

    # Evaluate f on part
    partial_result = numpy.array([f(pi) for pi in part],dtype=dtype)
    #print "f(v)",comm.rank, part 

    # Collect results
    if comm.rank == root:
        result = whole if inplace else numpy.empty(n,dtype=dtype)
    else:
        result = None

    comm.Barrier()
    comm.Gatherv((partial_result,mpitype), 
                 (result,(size,offset),mpitype), 
                 root=root)
    comm.Barrier()
    return result

def expensive(x):
    import random
    #t = time.time()
    #while time.time() < t+1: pass
    #A = numpy.random.rand(1000,1000)
    #for _ in range(2): B = numpy.dot(A,A)
    A = [random.random() for _ in range(1000)]
    A = [sum(vi*vj for vi in A) for vj in A]
    return x

def main():
    if comm.rank == 0: print "pool size",comm.size
    a = numpy.arange(128,dtype='d') if comm.rank == 0 else None
    #fn = lambda x:x*x
    fn = expensive
    result = mpimap(fn,a) if comm.size > 1 else numpy.array(map(fn,a))
    if comm.rank == 0: print result

if __name__ == "__main__":
    main()
