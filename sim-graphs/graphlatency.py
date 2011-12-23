
from configs import *
from simutils import *
from pylab import *
import matplotlib as mpl


rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})


N=3
R=1
W=1
k=1
iters = 10000

mpl.rcParams['figure.figsize'] = 6,2.5
mpl.rcParams['font.size'] = 18
mpl.rcParams['figure.subplot.bottom'] = .25
mpl.rcParams['figure.subplot.left'] = .14
mpl.rcParams['figure.subplot.right'] = .95
mpl.rcParams['lines.markersize'] = 12
mpl.rcParams['lines.linewidth'] = 1.5



readlats = {}
writelats = {}

for i in range(1, 4):
    R=i
    W=i
    for config in configs:
        run_sim(N, R, W, k, iters, 100000, 10, config.simparams, "LATS", "latencies.txt")
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
        
    figtext(.17, .80, "R=%d" % (R), size="large")
        
    if(R==2):
        xlabel("Read Latency (ms)", fontsize="large")
    if(R==1):
        ylabel("CDF", fontsize="large")
    
    semilogx()
        
    xlim(xmin=.01, xmax=1000)
    #this is just to get rid of the 000 at the bottom of the graph
    ylim(ymin=.00001)

    #legend(loc="lower left")

    savefig("readlats-%d.pdf" % (R))

    clf()

    for config in configs:
        plot(writelats[config][1], writelats[config][0], config.markerfmt[1:], color=config.color)
        
        plot([writelats[config][1][i] for i in range(10, len(writelats[config][1]), 15)], [writelats[config][0][i] for i in range(10, len(writelats[config][0]), 15)], config.markerfmt[:1], color=config.color)

        plot([writelats[config][1][0]], [writelats[config][0][0]], config.markerfmt, label=config.name, color=config.color)

    figtext(.17, .80, "W=%d" % (W), size="large")

    if(W==2):
        xlabel("Write Latency (ms)", fontsize="large")
    if(W==1):
        ylabel("CDF", fontsize="large")

    xlim(xmin=.01, xmax=1000)

    #this is just to get rid of the 000 at the bottom of the graph
    ylim(ymin=.00001)

    semilogx()


    savefig("writelats-%d.pdf" % (W))
    clf()


fig = figure()
figlegend = figure(figsize=(2.25*len(configs), .25))
ax = fig.add_subplot(111)
lines = []
for config in configs:
    lines.append(ax.plot([0],[0], config.markerfmt, label=config.name, color=config.color))
figlegend.legend(lines, [config.name for config in configs], loc="center", ncol=len(configs))
figlegend.savefig('latlegend.pdf')
    

