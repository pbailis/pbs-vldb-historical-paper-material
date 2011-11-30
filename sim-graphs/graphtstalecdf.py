
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

for R in [1, 2]:
    for W in [1, 2]:
        if R+W > N:
            continue
        for config in configs:
            run_sim(N, R, W, k, iters, writespacing, readsperwrite, config.simparams, "SWEEP", "tstale.txt")
            t = []
            stale = []

            for line in open("tstale.txt"):
                line = line.split()
                t.append(float(line[1]))
                stale.append(float(line[0]))
            results[config] = [t, stale]

        for config in configs:
            plot(results[config][0], results[config][1], config.markerfmt[1:], label=config.name, color=config.color)

        xlabel("t-visibility (ms)")
        #ylabel(r"$1-p_{stale}$")
        ylabel("Probability of Strong Consistency")
        title("N=%d R=%d W=%d" % (N, R, W))
        #ylim(ymin=.65)
        ax = gca()
        ax.set_xscale('symlog')
        xlim(xmax=100)

        legend(loc="lower right")
        savefig("tstales-%dN%dR%dW.pdf" % (N, R, W))
        cla()

