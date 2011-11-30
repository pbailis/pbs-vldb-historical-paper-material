
from configs import *
from simutils import *
from pylab import *

rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})


N=3
R=1
W=1
k=1
iters = 10000

readlats = {}
writelats = {}

for i in range(1, 3):
    R=i
    W=i
    for config in configs:
        run_sim(N, R, W, k, iters, 10000, 10, config.simparams, "LATS", "latencies.txt")
        wpcts = []
        wlats = []
        rpcts = []
        rlats = []
        
        for line in open("latencies.txt"):
            if line == "WRITE\n":
                whichpcts = wpcts
                whichlats = wlats
            elif line == "READ\n":
                whichpcts = rpcts
                whichlats = rlats
            else:
                line = line.split()
                whichpcts.append(float(line[0]))
                whichlats.append(float(line[1]))
        
        readlats[config] = [rpcts, rlats]
        writelats[config] = [wpcts, wlats]

    for config in configs:
        plot(readlats[config][1], readlats[config][0], config.markerfmt[1:], color=config.color)

        plot([readlats[config][1][i] for i in range(10, len(readlats[config][1]), 15)], [readlats[config][0][i] for i in range(10, len(readlats[config][0]), 15)], config.markerfmt[:1], color=config.color)
        
        plot([readlats[config][1][0]], [readlats[config][0][0]], config.markerfmt, label=config.name, color=config.color)
        
    figtext(.14, .88, "R=%d" % (R), size="x-large")
        
    xlabel("Read Latency (ms)")
    ylabel("CDF")
    
    semilogx()
        
    #legend(loc="lower left")
    savefig("readlats-%d.pdf" % (R))

    clf()

    for config in configs:
        plot(writelats[config][1], writelats[config][0], config.markerfmt[1:], color=config.color)
        
        plot([writelats[config][1][i] for i in range(10, len(writelats[config][1]), 15)], [writelats[config][0][i] for i in range(10, len(writelats[config][0]), 15)], config.markerfmt[:1], color=config.color)

        plot([writelats[config][1][0]], [writelats[config][0][0]], config.markerfmt, label=config.name, color=config.color)

    figtext(.14, .88, "W=%d" % (W), size="x-large")

    xlabel("Write Latency (ms)")
    ylabel("CDF")

    semilogx()

    if(W==1):
        legend(loc="lower left")
    savefig("writelats-%d.pdf" % (W))
    clf()

    

