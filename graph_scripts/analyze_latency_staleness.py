

from plot_utils import *
from math import ceil
from pylab import *

results = fetch_results(resultsfile)

percentile = .99

def ktocolor(k):
    if k == 0:
        return 'black'
    if k == 1:
        return 'blue'
    if k == 2:
        return 'green'

def plot_with_errorbars(k, result, percentile):
    ktresult = get_latency_staleness_results(k, result, percentile)
    if ktresult != None:
        plot_with_errorbars_internal(ktresult)

print "N R W k t pstale"

ktstales = []

for result in results:
    for k in range(1, 4):
        ktstale = get_latency_staleness_results(k, result, percentile)
        if ktstale != None:
            ktstales.append(ktstale)
            print "%d %d %d %f %d %f %f %f" % (ktstale.config.N,
                                               ktstale.config.R,
                                               ktstale.config.W,
                                               ktstale.config.lmbda,
                                               ktstale.kstale,
                                               ktstale.tstale,
                                               ktstale.pstale,
                                               ktstale.latency)

lmbdas = set()
for kt in ktstales:
    lmbdas.add(kt.config.lmbda)

for lmbda in lmbdas:
    for k in range(1, 2):
        matching_k = [kt for kt in ktstales if kt.kstale == k 
                      and kt.config.lmbda == lmbda]
        matching_k.sort(key=lambda kt : kt.tstale)

        plot([kt.tstale for kt in matching_k],
             [kt.latency for kt in matching_k],
             'o-', label=str(lmbda))

        for kt in matching_k:
            text(kt.tstale,
                 kt.latency,
                 "%dR%dW" % (kt.config.R, kt.config.W))

ax=gca()
ax.set_xscale('symlog', linthreshx=.01)
#ax.set_yscale('log')

legend()
show()

