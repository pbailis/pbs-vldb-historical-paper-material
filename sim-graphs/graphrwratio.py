
from configs import *
from simutils import *
from pylab import *
import matplotlib as mpl

mpl.rcParams['font.size'] = 16
mpl.rcParams['lines.markersize'] = 6
mpl.rcParams['lines.linewidth'] = 1.2
mpl.rcParams['figure.subplot.bottom'] = .17
mpl.rcParams['figure.subplot.left'] = .12

N=3
R=1
W=1
k=1
iters = 10000
writespacing = 10000
readsperwrite = 10

results = {}

wlambdas = [.1, .2, .5, 1, 2, 4]

colors = ["red", "green", "blue", "black", "magenta", "cyan"]
markers = ['o-', 's-', 'h-', '^-', '*-', 'D-']
markertimes = [1, 3, 5, 7, 9]


reverserange = range(0, len(wlambdas))
reverserange.reverse()
for i in reverserange:
    wlambda = wlambdas[i]
    fine = ""
    if wlambda >= 2:
        fine = "F"

    run_sim(N, R, W, k, iters, writespacing, readsperwrite, "EXPONENTIAL %f 1 %s" % (wlambda, fine), "SWEEP", "tstale.txt")
    t = []
    stale = []

    print wlambda
    for line in open("tstale.txt"):
        line = line.split()
        print line[1], line[0]
        t.append(round(float(line[1]),5))
        stale.append(float(line[0]))
    
    if int(wlambda) == wlambda:
        wlambda = "%d" % int(wlambda)
    else:
        wlambda = "%f" % (wlambda)
        wlambda = wlambda[:4]

    plot(t, stale, color = colors[i])
    
    mt = [time for time in markertimes if time in t]
    for time in mt:
        plot([t[time]], [stale[time]], markers[i], color=colors[i])

    tindex = t.index(markertimes[0])

    plot([t[tindex]], [stale[tindex]], markers[i], label="1:%s" % (wlambda), color=colors[i])


xlabel("t-visibility (ms)")
ylabel("P(consistency)")
ax = gca()
#ax.set_xscale('symlog')

xlim(xmax=10)

legend(loc="lower right", title=r"ARS$\lambda$:W$\lambda$", ncol=2)


savefig("rwratio.pdf")
cla()

