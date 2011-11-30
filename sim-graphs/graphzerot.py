
from configs import *
from simutils import *
from pylab import *

N=3
R=1
W=1
k=1
sweepiters = 1000
latiters = 10000
writespacing = 10000

lat_pct = .999

results = {}

figure(figsize=(10, 10))

class LatStaleResult:
    def __init__(self, lat, t, label, ps):
        self.latency = lat
        self.t = t
        self.label = label
        self.ps = ps


for R in range(1, N+1):
    for W in range(1, N+1):
        if R+W > N+1:
            continue
        for config in configs:
            if config not in results:
                results[config] = []


            t = -1
            run_sim(N, R, W, k, sweepiters, writespacing, 10, config.simparams, "SWEEP", "tstale.txt")
            for line in open("tstale.txt"):
                line = line.split()
                stale = float(line[0])
                t = float(line[1])
                if t == 0:
                    break

            if t != 0:
                print "DIDN'T FIND T-STALE"
                exit(-1)

            run_sim(N, R, W, k, latiters, writespacing, 10, config.simparams, "LATS", "latencies.txt")

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

            res = LatStaleResult(wlat+rlat, t, "%dR%dW" % (R, W), stale)
            
            results[config].append(res)
            



for config in configs:
    r = results[config]
    r.sort(key=lambda x: x.ps)
    plot([res.ps for res in r], [res.latency for res in r], config.markerfmt, label=config.name, color=config.color)
    for res in r:
        text(res.ps, res.latency, res.label)

xlabel("Probability of Strong Consistency 0ms after Commit")
ylabel("99.9th Percentile Read and Write Latency")
ax = gca()

ax.set_yscale("log")

xlim(xmax=1.05)

legend(loc="upper left")
savefig("latency-ps.pdf")



