
from configs import *
from simutils import *
from pylab import *

mpl.rcParams['font.size'] = 16
mpl.rcParams['figure.subplot.bottom'] = .17
mpl.rcParams['figure.subplot.top'] = .92
mpl.rcParams['figure.subplot.left'] = .14
mpl.rcParams['figure.subplot.right'] = .95
mpl.rcParams['lines.markersize'] = 12
mpl.rcParams['lines.linewidth'] = 1.5
mpl.rcParams['legend.fontsize'] = 20

graphcutoffpct = .99

N=3
R=1
W=1
k=1
iters = 100000
writespacing = 10000
readsperwrite = 10

results = {}

Ns = [2,3,5,10]
markers = ['o-', 's-', 'h-', '^-', '*-', 'D-']
markerpos = range(2, 100, 2)
colors = ["red", "green", "blue", "black", "magenta", "cyan"]

for config in configs:
    if config.name == "LNKD-SSD":
        config.simparams += " F"
    config.simparams = config.simparams+" M "
    maxt = -1
    for i in range(0, len(Ns)):
        N = Ns[i]

        run_sim(N, R, W, k, iters, writespacing, readsperwrite, config.simparams, "SWEEP", "tstale.txt")
        t = []
        stale = []


        thiscutoff = -1

        cutindx = 0
        for line in open("tstale.txt"):
            if thiscutoff == -1:
                cutindx+=1
            line = line.split()
            thist = float(line[1])
            thisstale = float(line[0])
            t.append(thist)
            stale.append(thisstale)

            if (thisstale > graphcutoffpct and config.name != "LNKD-SSD") or thisstale > .999:
                if thiscutoff != -1:
                    continue
                thiscutoff = thist
                if thist > maxt:
                    maxt = thist


        plot(t, stale, markers[i][1:], color=colors[i])

        step = max(1, int(cutindx/10.0))
        for mpos in range(1, len(t), step):
            plot(t[mpos], stale[mpos], markers[i], color=colors[i])
        plot(t[1], stale[1], markers[i], color=colors[i], label=str(N))

    if config.name == "LNKD-SSD":
        xlabel("t-visibility (ms)", fontsize=20)
    if config.name == "LNKD-DISK":
        ylabel("P(Consistency)", fontsize=20)
    ax = gca()

    if maxt != -1:
        xlim(xmax=maxt)
    xlim(xmin=.00001)

    title(config.name)
    if config.name == "LNKD-DISK":
        legend(loc="lower right", title="N")
    savefig("sweepn-%s.pdf" % (config.name))
    cla()

