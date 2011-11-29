from math import log, floor
from random import random
from pylab import *


linkedin_ssd_latencies = [15, 25]
linkedin_ssd_pcts = [.95, .99]


def get_exponential(lmbda):
    return log(1-random())/(-lmbda)

def get_pareto(alpha, m):
    r = pow(random(), 1/alpha)

    if r == 0:
        return 10000000000

    return m/r

def get_samples(l1, m1,  l2, m2):
    samples = []

    for i in range(0, 10000):
        lats = []
        for r in range(0, 3):
            lats.append(get_pareto(l1, m1)+get_pareto(l2, m2))
        lats.sort()
        samples.append(lats[0])

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
        toterr += pow(err,2)

    err = average(samples)-4.58
    if err < 0:
        return -10000

    toterr += pow(err, 2)

    return toterr

minerr = 100000
bestm = -1
bestl = -1
for m in xrange(300, 400):
    m = m/100.0
    for l in xrange(75, 90):
        l = l/100.0

        test = get_samples(l, m, .9, .15)
        err = get_error(test, linkedin_ssd_latencies, linkedin_ssd_pcts)
        if err < 0:
            break
        if err < minerr:
            bestm = m
            bestl = l
            minerr = err
     
        print  l, m, err

print "BEST:", bestl, bestm, minerr

test=get_samples(3.75, 3.1, .9, .15)
plot(linkedin_ssd_latencies,linkedin_ssd_pcts,  'o-', label="REAL", color="green")
plot([get_pct(test, pct) for pct in linkedin_ssd_pcts], linkedin_ssd_pcts, 'o-', label="PREDICT", color="blue")

plot([4.58], [.5], "o", color="green")
plot([average(test)], [.5], "o", color="blue")


title("YAMMER READ")
legend(loc="lower right")
ylabel("CDF")
xlabel("latency (ms)")
show()
