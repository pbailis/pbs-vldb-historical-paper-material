
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

markertimes = [1, 2, 3, 4,5,7,9,11,12.5,15,20,30,40,50,60,75,90]

mpl.rcParams['font.size'] = 16
mpl.rcParams['figure.subplot.bottom'] = .17
mpl.rcParams['figure.subplot.top'] = .92
mpl.rcParams['figure.subplot.left'] = .14
mpl.rcParams['figure.subplot.right'] = .95
mpl.rcParams['lines.markersize'] = 12
mpl.rcParams['lines.linewidth'] = 1.5

for R in [1, 2]:
    for W in [1, 2]:
        if R+W > N:
            continue
        for config in configs:
            run_sim(N, R, W, k, iters, writespacing, readsperwrite, config.simparams, "SWEEP", "tstale.txt")
            save_data(N, R, W, k, iters, writespacing, readsperwrite, config.simparams, "SWEEP")
            t = []
            stale = []

            print config.name
            for line in open("tstale.txt"):
                line = line.split()
                t.append(float(line[1]))
                stale.append(float(line[0]))
                print line[1], line[0]

            results[config] = [t, stale]

        for config in configs:
            t = results[config][0]
            stale = results[config][1]


            plot(t, stale, config.markerfmt[1:], color=config.color)

            mt = [time for time in markertimes if time in t]

            for time in mt:
                plot([t[time]], [stale[time]], config.markerfmt, color=config.color)

            tindex = t.index(markertimes[0])
            plot([t[tindex]], [stale[tindex]], config.markerfmt, label=config.name, color=config.color)

        if R==2 and W==1:
            xlabel("t-visibility (ms)", fontsize=20)
        #ylabel(r"$1-p_{stale}$")
        if R==1 and W==1:
            ylabel("P(consistency)", fontsize=20)
        title("N=%d R=%d W=%d" % (N, R, W))
        #ylim(ymin=.65)
        ax = gca()
        ax.set_xscale('symlog')
        xlim(xmax=100)
        ylim(ymax=1.0)

        #if R==W and R==1:
        #    legend(loc="lower right", bbox_to_anchor=(.9, .12))
        savefig("tstales-%dN%dR%dW.pdf" % (N, R, W))
        cla()

