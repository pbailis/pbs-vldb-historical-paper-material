
from configs import *
from simutils import *
from pylab import *

N=3
R=1
W=1
k=1
iters = 50000
writespacing = 10000

ps = .001
lat_pct = .999

results = {}

class LatStaleResult:
    def __init__(self, wlat, rlat, t, label):
        self.t = t
        self.label = label
        self.wlat = wlat
        self.rlat = rlat


for R in range(1, N+1):
    for W in range(1, N+1):
        if R+W > N+1:
            continue
        for config in configs:
            if config.name == "YMMR":
                simparams = config.simparams+" L "
            else:
                simparams = config.simparams
            if config not in results:
                results[config] = []

            t = 0
            if R+W <= N:
                t == -1
                run_sim(N, R, W, k, iters, writespacing, 10, simparams, "SWEEP", "tstale.txt")
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

            run_sim(N, R, W, k, iters*20, writespacing, 10, config.simparams, "LATS", "latencies.txt")


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

            res = LatStaleResult(wlat, rlat, t, "$R$$=$$%d$, $W$$=$$%d$" % (R, W))
            
            results[config].append(res)
            



for config in configs:
    r = results[config]
    r.sort(key=lambda x: x.t)
    plot([res.t for res in r], [res.rlat+res.wlat for res in r], config.markerfmt, label=config.name, color=config.color)
    for res in r:
        text(res.t, res.rlat+res.wlat, res.label)

r = results[configs[0]]
r.sort(key=lambda x : x.label)
for res in r:
    if res != r[0]:
        print '&',
    print res.label, 
print "\\\\"

labels = ["$R$$=$$%d$, $W$$=$$%d$" % (d[0], d[1]) for d in [(1, 1), (1, 2), (2, 1), (2,2), (3,1),(1,3)]]

for label in labels:
    print "\multicolumn{1}{|c|}{%s}" % (label)
    for config in configs:
        res = [c for c in results[config] if c.label==label][0]
        print '&', round(res.rlat,2),'&', round(res.wlat,2), '&', "0" if res.t == 0 else res.t,
    print '\\\\'

print '\hline'

xlabel("t-visibility (ms)")
ylabel("99.9th Percentile Read and Write Latency")
title("p_staler = .001")
ax = gca()

ax.set_xscale("symlog")
ax.set_yscale("symlog")

legend(loc="lower right")
savefig("latency-tstale.pdf")



