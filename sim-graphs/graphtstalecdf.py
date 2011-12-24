
from configs import *
from simutils import *
from pylab import *
import matplotlib as mpl

N=3
R=1
W=1
k=1
iters = 100000
writespacing = 0
readsperwrite = 0

results = {}


mpl.rcParams['font.size'] = 16
mpl.rcParams['figure.subplot.bottom'] = .10
mpl.rcParams['figure.subplot.top'] = .92
mpl.rcParams['figure.subplot.left'] = .10
mpl.rcParams['figure.subplot.right'] = .96
mpl.rcParams['lines.markersize'] = 12
mpl.rcParams['lines.linewidth'] = 1.5

RWs = [(1,1), (1,2), (2,1)]
markers = ['^-', 'o-', 's-', 'v-', '*-', 'D-']
colors = ["red", "green", "blue", "black", "magenta", "cyan"]

configmaxes = {"YMMR":1000, "LNKD-DISK":100, "LNKD-SSD":2.4, "WAN":110}

for config in configs:
    if config.name == "YMMR":
        markertimes = [0, 1, 3, 5, 10, 20, 35, 50, 100, 200, 280, 400, 700, 1000]
        simparams = config.simparams+" L "
    elif config.name == "LNKD-SSD":
        markertimes = [i/100.0 for i in range(0, 240, 10)]
        simparams = config.simparams+" F "        
    elif config.name == "LNKD-DISK":
        markertimes = [0, 1, 2, 3, 4,5,7,9,11,12.5,15,20,30,40,50,60,75,90]
        simparams = config.simparams
    else:
        simparams = config.simparams
        markertimes = [0, 1, 2, 3, 4,5,7,9,11,12.5,15,20,30,40,50,60,75,90]

    for i in range(0, len(RWs)):
        rw = RWs[i]
        run_sim(3, rw[0], rw[1], k, iters, writespacing, readsperwrite, simparams, "SWEEP", "tstale.txt")
        t = []
        stale = []

        print config.name
        for line in open("tstale.txt"):
            line = line.split()
            t.append(round(float(line[1]), 2))
            stale.append(float(line[0]))
            print line[1], line[0]

        plot(t, stale, config.markerfmt[1:], color=colors[i])

        mt = [time for time in markertimes if time in t]

        for time in mt:
            time = t.index(time)
            plot([t[time]], [stale[time]], markers[i], color=colors[i])

        tindex = t.index(mt[0])
        plot([t[tindex]], [stale[tindex]], markers[i], label="R=%d, W=%d" % (rw[0], rw[1]), color=colors[i])


    ax = gca()
    if config.name != "LNKD-SSD":
        ax.set_xscale('symlog')
    title(config.name, fontsize=20)
    xlim(xmax=configmaxes[config.name])
    ylim(ymax=1.0)

        #if R==W and R==1:
        #    legend(loc="lower right", bbox_to_anchor=(.9, .12))
    savefig("tstales-%s.pdf" % (config.name))
    cla()

cla()
fig = figure()
fl = figure(figsize=(2.25*len(RWs), .25))
ax = fig.add_subplot(111)
lines = []
for i in range(0, len(RWs)):
    lines.append(ax.plot([0],[0], markers[i], label="R=%d, W=%d" % (rw[0], rw[1]), color=colors[i]))
fl.legend(lines, ["R=%d W=%d" % (rw[0], rw[1]) for rw in RWs],  ncol=len(configs), loc="center", bbox_to_anchor=(.53,.5))
fl.show()
fl.savefig('stalelegend.pdf')


'''
    if config.name == "YMMR":
        xlabel("t-visibility (ms)", fontsize=20)
    #ylabel(r"$1-p_{stale}$")
    if config.name == "LNKD-SSD":
        ylabel("P(consistency)", fontsize=20)
'''
