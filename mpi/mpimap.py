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

def queuemap(f, a, root=0, inplace=False):
    WORK_TAG=1
    DONE_TAG=2
    if comm.rank == root:
        # TODO: let master do work so small cluster performance doesn't suffer
        npoints = a.size
        nworkers = comm.size - 1
        result = numpy.empty(npoints, dtype='d')
        worker_id = list(range(1,nworkers+1))
        active_point = {}
        ntail = min(npoints,nworkers)
        # block spread initial values across workers
        requests = []
        for i in range(ntail):
            worker = worker_id[i]
            active_point[worker] = i
            #print("root: sending %d to %d"%(i,worker))
            requests.append(comm.Isend(a[i:i+1], dest=worker, tag=WORK_TAG))
        for r in requests: r.Wait()
        # recv/send until no more work
        for i in range(ntail,npoints):
            status = MPI.Status()
            comm.Probe(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            worker = status.source
            pt = active_point[worker]
            #print("root: receiving %d from %d and sending %d"%(pt,worker,i))
            comm.Recv(result[pt:pt+1], source=worker, tag=status.Get_tag())
            active_point[worker] = i
            comm.Send(a[i:i+1], dest=worker, tag=WORK_TAG)
        # wait for outstanding work
        for _ in range(ntail):
            status = MPI.Status()
            comm.Probe(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            worker = status.source
            pt = active_point[worker]
            #print("root: receiving %d from %d and not sending any more"%(pt,worker))
            comm.Recv(result[pt:pt+1], source=worker, tag=status.tag)
        # block tell workers they are done by sending a bad point
        stop = numpy.zeros(1, 'd')
        requests = []
        for worker in worker_id:
            #print("root: let worker %d know we are done"%(worker,))
            requests.append(comm.Isend(stop, worker, tag=DONE_TAG))
        for r in requests: r.Wait()
        return result

    else:
        # loop until no more work
        point = numpy.empty(1, dtype='d')
        while True:
            status = MPI.Status()
            comm.Probe(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
            comm.Recv(point, source=root, tag=status.tag)
            if status.tag==DONE_TAG: break
            #print("%d: receiving point %g"%(comm.rank,point[0]))
            result = f(point[0])
            #print("%d: sending result %g"%(comm.rank,result))
            comm.Send(result, dest=root)

        return None   # return value is ignored

def expensive(x):
    import random
    #t = time.time()
    #while time.time() < t+1: pass
    #A = numpy.random.rand(1000,1000)
    #for _ in range(2): B = numpy.dot(A,A)
    A = [random.random() for _ in range(1000)]
    A = [sum(vi*vj for vi in A) for vj in A]
    return x

def random_sleep(x):
    print("%d: sleep %d"%(comm.rank,x))
    time.sleep(x)
    return x

def main():
    if comm.rank == 0: print "pool size",comm.size
    a = None
    if comm.rank == 0:
        numpy.random.seed(20)
        a = numpy.asarray(numpy.random.poisson(1.0,size=20),'d')
        #a = numpy.arange(20,dtype='d')
        #a = numpy.arange(2048,dtype='d')
    #fn = lambda x:x*x
    #fn = expensive
    fn = random_sleep
    if comm.size > 1:
        #result = mpimap(fn,a)
        result = queuemap(fn,a)
    else:
        result = numpy.array(map(fn,a))
    if comm.rank == 0: print sum(result)

if __name__ == "__main__":
    main()
