
from configs import *
from simutils import *
from pylab import *

N=3
R=1
W=1
k=1
iters = 1000
writespacing = 10000
readsperwrite = 10

results = {}

for N in [3,5,10,100]:
    for config in configs:
        if config.name != "LNKD-DISK":
            continue
        run_sim(N, R, W, k, iters, writespacing, readsperwrite, config.simparams, "SWEEP", "tstale.txt")
        t = []
        stale = []

        for line in open("tstale.txt"):
            line = line.split()
            t.append(float(line[1]))
            stale.append(float(line[0]))
            results[config] = [t, stale]
            
        plot(results[config][0], results[config][1], label=str(N))

xlabel("t-visibility (ms)")
#ylabel(r"$1-p_{stale}$")
ylabel("Probability of Strong Consistency")
ax = gca()
ax.set_xscale('symlog')

legend(loc="lower right", title="N")
savefig("sweepn.pdf")

