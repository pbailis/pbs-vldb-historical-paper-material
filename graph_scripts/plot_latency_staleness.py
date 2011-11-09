

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
    for k in range(1, 4):
        plot_with_errorbars(k, result, percentile)

    N = result.config.N

legend()

title("N=%d, p_staler = %f" % (N, 1.0-percentile))
xlabel("t-staleness (ms)")
ylabel("average write + read latency (ms)")
savefig("latency-stale.pdf")

show()
