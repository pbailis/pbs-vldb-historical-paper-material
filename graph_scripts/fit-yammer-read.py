from math import log, floor
from random import random
from pylab import *


yammer_read_latencies = [3.75, 4.17, 5.20, 6.045, 6.59]
yammer_read_pcts = [.5, .75, .95, .98, .99]


def get_exponential(lmbda):
    return log(1-random())/(-lmbda)

def get_pareto(alpha, m):
    return m/pow(random(), 1/alpha)

def get_samples(l1, l2):
    samples = []

    
    for i in range(0, 100000):
        lats = []
        for r in range(0, 3):
            lats.append(get_pareto(l1, 1.55/1.1)+get_pareto(l2, 1.55/1.1))
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
            print pcts[i], err
            return -10000
        toterr += pow(err, 2)

    return toterr

for i in range(295, 310):
    continue
    l = i/100.0
    test = get_samples(l, l)
    print l, get_error(test, yammer_read_latencies, yammer_read_pcts)

test=get_samples(2.97, 2.97)
print min(test)
plot(yammer_read_latencies,yammer_read_pcts,  'o-', label="REAL")
plot([get_pct(test, pct) for pct in yammer_read_pcts], yammer_read_pcts, 'o-', label="PREDICT")
title("YAMMER READ")
legend(loc="lower right")
ylabel("CDF")
xlabel("latency (ms)")
show()
