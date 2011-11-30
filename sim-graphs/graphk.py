
from configs import *
from simutils import *
from pylab import *

N=3
R=1
W=1
k=1
iters = 1000
readsperwrite = 10
writespacing = 10

ps = .01

results = {}

class LatStaleResult:
    def __init__(self, lat, t, label):
        self.latency = lat
        self.t = t
        self.label = label

writespaces = [5]

for config in configs:
    if config.name != "YMMR":
        continue
    results[config] = []
    for k in range(1, 3):
        ts = []
        stales = []
        run_sim(N, R, W, k, iters, writespacing, readsperwrite, config.simparams,  "SWEEP", "tstale.txt")
        for line in open("tstale.txt"):
            line = line.split()
            stale = float(line[0])
            t = float(line[1])

            ts.append(t)
            stales.append(stale)
            results[config].append(t)
            
        plot(ts, stales, config.markerfmt, label=str(k))

xlabel("t-visibility (ms)")
ylabel("p_s")
title("N=3, R=W=1")
xlim(xmax=20)
ax = gca()

legend(loc="lower right", title="k")
savefig("kstale.pdf")
show()


