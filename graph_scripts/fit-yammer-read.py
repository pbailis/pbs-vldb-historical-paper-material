from math import log, floor
from random import random
from pylab import *


yammer_read_latencies = [3.75, 4.17, 5.20, 6.045, 6.59]
yammer_read_pcts = [.5, .75, .95, .98, .99]


def get_exponential(lmbda):
    return log(1-random())/(-lmbda)

def get_pareto(alpha, m):
    r = pow(random(), 1/alpha)

    if r == 0:
        return 10000000000

    return m/r

def get_samples(l1, m1, l2, m2):
    samples = []

    
    for i in range(0, 10000):
        lats = []
        for r in range(0, 3):
            lats.append(get_pareto(l1, m1)+get_pareto(l2, m2))
        lats.sort()
        samples.append(lats[1])

    samples.sort()
    return samples

def get_pct(samples, pct):
    return samples[int(floor((len(samples)-1)*pct))]

def get_error(samples, real, pcts):
    toterr= 0
    for i in range(0, len(pcts)):
        err = get_pct(samples, pcts[i])-real[i]
        #print pcts[i], real[i], get_pct(samples, pcts[i])
        if err < 0:
            return -10000
        toterr += pow(err, 2)

    return toterr

besterr = 100000
bestm = -1
bestl = -1

for m in range(1375, 1390):
    m = m/1000.0
    for l in range(2860, 2875):
        l = l/1000.0
        test = get_samples(l, m, l, m)
        err = get_error(test, yammer_read_latencies, yammer_read_pcts)
        if err < 0:
            break
        if err < besterr:
            besterr = err
            bestm = m
            bestl = l
        print l, m, err

print "BEST:", bestl, bestm, besterr

test=get_samples(2.866, 1.385, 2.866, 1.385)
print min(test)
plot(yammer_read_latencies,yammer_read_pcts,  'o-', label="REAL")
plot([get_pct(test, pct) for pct in yammer_read_pcts], yammer_read_pcts, 'o-', label="PREDICT")
title("YAMMER READ")
legend(loc="lower right")
ylabel("CDF")
xlabel("latency (ms)")
show()
