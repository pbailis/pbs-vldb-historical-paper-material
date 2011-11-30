
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
                

            run_sim(N, R, W, k, iters, writespacing, readsperwrite, config.simparams, "WORSTCASE", "tstale.txt")
            wt = []
            wstale = []

            for line in open("tstale.txt"):
                line = line.split()
                wt.append(float(line[1]))
                wstale.append(float(line[0]))
        
            results[config] = [t, stale, wt, wstale]

        for config in configs:
            plot(results[config][0], results[config][1], config.markerfmt[1:], label=config.name, color=config.color)
            plot(results[config][2], results[config][3], '--', color=config.color)

        xlabel("t-visibility (ms)")
        ylabel("1-p_stale")
        title("N=%d R=%d W=%d" % (N, R, W))
        #ylim(ymin=.65)
        semilogx()

        legend(loc="lower right")
        savefig("worstcase-%dN%dR%dW.pdf" % (N, R, W))
        cla()

