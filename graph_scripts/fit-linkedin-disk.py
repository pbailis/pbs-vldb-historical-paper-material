from math import log, floor
from random import random
from pylab import *


linkedin_disk_latencies = [15, 25]
linkedin_disk_pcts = [.95, .99]


def get_exponential(lmbda):
    return log(1-random())/(-lmbda)

def get_pareto(alpha, m):
    r = pow(random(), 1/alpha)

    if r == 0:
        return 10000000000

    return m/r

def get_samples(l1, l2):
    samples = []

    for i in range(0, 100000):
        lats = []
        lats.append(get_exponential(l1)+get_exponential(l2))
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
for l in xrange(1860, 1870,):
    l = l/10000.0
    
    test = get_samples(l, 3.28)
    err = get_error(test, linkedin_disk_latencies, linkedin_disk_pcts)
    if err < minerr:
        bestl = l
        minerr = err
        
    print  l, err

print "BEST:", bestl, minerr

test=get_samples(.1861, 3.28)
plot(linkedin_disk_latencies,linkedin_disk_pcts,  'o-', label="REAL", color="green")
plot([get_pct(test, pct) for pct in linkedin_disk_pcts], linkedin_disk_pcts, 'o-', label="PREDICT", color="blue")

plot([4.58], [.5], "o", color="green")
plot([average(test)], [.5], "o", color="blue")

print get_pct(test, .999)
print max(test)


title("YAMMER READ")
legend(loc="lower right")
ylabel("CDF")
xlabel("latency (ms)")
show()
