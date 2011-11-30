
from configs import *
from simutils import *
from pylab import *

N=3
R=1
W=1
k=1
iters = 1000
writespacing = 10000

ps = .001
lat_pct = .999

results = {}

class LatStaleResult:
    def __init__(self, lat, t, label):
        self.latency = lat
        self.t = t
        self.label = label


for R in range(1, N+1):
    for W in range(1, N+1):
        if R+W > N+1:
            continue
        for config in configs:
            if config not in results:
                results[config] = []


            t = -1
            run_sim(N, R, W, k, iters, writespacing, 10, config.simparams, "SWEEP", "tstale.txt")
            for line in open("tstale.txt"):
                line = line.split()
                stale = float(line[0])
                if stale >= 1-ps:
                    t = float(line[1])
                    print stale, t
                    break

            if t == -1:
                print "DIDN'T FIND T-STALE"
                exit(-1)

            run_sim(N, R, W, k, iters, writespacing, 10, config.simparams, "LATS", "latencies.txt")

            writes = True
            wlat = -1
            rlat = -1
            for line in open("latencies.txt"):
                if line.find(' ') == -1:
                    continue
                line = line.split()
                pct = float(line[0])
                if pct == lat_pct:
                    if writes:
                        wlat = float(line[1])
                        writes = False
                    elif wlat != -1:
                        rlat = float(line[1])

            if wlat == -1:
                print "DIDNT FIND MATCHING WRITE LATENCY"
                exit(-1)

            if rlat == -1:
                print "DIDNT FIND MATCHING WRITE LATENCY"
                exit(-1)

            res = LatStaleResult(wlat+rlat, t, "%dR%dW" % (R, W))
            
            results[config].append(res)
            



for config in configs:
    r = results[config]
    r.sort(key=lambda x: x.t)
    plot([res.t for res in r], [res.latency for res in r], config.markerfmt, label=config.name, color=config.color)
    for res in r:
        text(res.t, res.latency, res.label)

xlabel("t-visibility (ms)")
ylabel("99.9th Percentile Read and Write Latency")
title("p_staler = .001")
ax = gca()

ax.set_xscale("symlog")
ax.set_yscale("symlog")

legend(loc="lower right")
savefig("latency-tstale.pdf")



