
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

markertimes = [1, 2, 3, 4,5,6,7,8,9,11,12.5,15,20,30,40,50,60,70,80,90]

for R in [1, 2]:
    for W in [1, 2]:
        if R+W > N:
            continue
        for config in configs:
            if config.name == "WAN":
                continue
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
            if config.name == "WAN":
                continue

            t = results[config][0]
            stale = results[config][1]

            plot(t, stale, config.markerfmt[1:], color=config.color)

            mt = [time for time in markertimes if time in t]

            for time in mt:
                plot([t[time]], [stale[time]], config.markerfmt, color=config.color)

            tindex = t.index(markertimes[0])
            plot([t[tindex]], [stale[tindex]], config.markerfmt, label=config.name, color=config.color)

            plot(results[config][2], results[config][3], '--', color=config.color, lw=2)

        xlabel("t-visibility (ms)")
        #ylabel("1-p_stale")
        ylabel("Probability of Strong Consistency")
        title("N=%d R=%d W=%d" % (N, R, W))
        #ylim(ymin=.65)
        semilogx()

        legend(loc="lower right")
        xlim(xmax=100)
        savefig("worstcase-%dN%dR%dW.pdf" % (N, R, W))
        cla()

