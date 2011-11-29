
from configs import *
from simutils import *
from pylab import *

N=3
R=1
W=1
k=1
iters = 10000

results = {}

for R in [1, 2]:
    for W in [1, 2]:
        if R+W > N:
            continue
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
            plot(results[config][1], results[config][0], config.markerfmt[1:], label=config.name, color=config.color)

        xlabel("t-visibility (ms)")
        ylabel("1-p_stale")
        title("N=%d R=%d W=%d" % (N, R, W))
        ylim(ymin=.65)
        semilogx()

        legend(loc="lower right")
        savefig("tstales-%dN%dR%dW.pdf" % (N, R, W))
        cla()

