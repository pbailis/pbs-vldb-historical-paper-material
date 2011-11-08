

from plot_utils import *
from math import ceil
from pylab import *

results = fetch_results(resultsfile)

percentile = .95

def ktocolor(k):
    if k == 0:
        return 'black'
    if k == 1:
        return 'blue'
    if k == 2:
        return 'green'

def plot_with_errorbars_internal(ktresult):
    errorbar(ktresult.tstale, ktresult.latency,
             fmt='o-',
             yerr=ktresult.latencydev,
             color=ktocolor(ktresult.kstale))
    text(ktresult.tstale, ktresult.latency, "%dN%dR%dW" % (ktresult.config.N,
                                                           ktresult.config.R, 
                                                           ktresult.config.W), fontsize=8)

def plot_with_errorbars(k, result, percentile):
    ktresult = get_latency_staleness_results(k, result, percentile)
    if ktresult != None:
        plot_with_errorbars_internal(ktresult)

print "N R W k t pstale"

for result in results:
    for k in range(0, 3):
        ktstale = get_latency_staleness_results(k, result, percentile)
        if ktstale != None:
            print "%d %d %d %f %d %f %f" % (ktstale.config.N,
                                            ktstale.config.R,
                                            ktstale.config.W,
                                            ktstale.config.lmbda,
                                            ktstale.kstale,
                                            ktstale.tstale,
                                            ktstale.pstale)


