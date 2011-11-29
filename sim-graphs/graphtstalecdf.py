
from configs import *
from simutils import *
from pylab import *

N=3
R=1
W=1
k=1
iters = 10000

results = {}

for config in configs:
    run_sim(N, R, W, k, iters, config.simparams, "SWEEP", "tstale.txt")
    t = []
    stale = []

    for line in open("tstale.txt"):
        line = line.split()
        t.append(float(line[0]))
        stale.append(float(line[1]))
        
    results[config] = [t, stale]

for config in configs:
    plot(results[config][1], results[config][0], config.markerfmt, label=config.name, color=config.color)

xlabel("t-visibility (ms)")
ylabel("1-p_stale")

legend(loc="lower right")
savefig("tstales.pdf")

