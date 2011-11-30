
from configs import *
from simutils import *
from pylab import *

N=3
R=1
W=1
k=1
iters = 10000

readlats = {}
writelats = {}

for config in configs:
    run_sim(N, R, W, k, iters, 1000, 10, config.simparams, "LATS", "latencies.txt")
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
    plot(readlats[config][1], readlats[config][0], config.markerfmt, label=config.name, color=config.color)

xlabel("Read latency (ms)")
ylabel("CDF")

legend(loc="lower right")
savefig("readlats.pdf")

cla()

for config in configs:
    plot(writelats[config][1], writelats[config][0], config.markerfmt, label=config.name, color=config.color)

xlabel("Write latency (ms)")
ylabel("CDF")

legend(loc="lower right")
savefig("writelats.pdf")

    
