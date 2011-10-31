
from plot_utils import *
from math import ceil
from pylab import *

results = fetch_results("../results/micro/5N-2011-10-30-15_20_59/")

percentile = .98

def ktocolor(k):
    if k == 0:
        return 'black'
    else:
        return 'blue'

def plot_with_errorbars(result):
    pctile_index = int(ceil(len(result.reads)*percentile))

'''
    chosen = result.reads[pctile_index]
    chosenlatency = average([r.latency for r in result.reads[:pctile_index]])+average([w.latency for w in result.writes])
    chosenlatencydev = sqrt(pow(std([r.latency for r in result.reads[:pctile_index]]), 2)+
                            pow(std([w.latency for w in result.writes]), 2))

    errorbar([chosen.tstale], [chosenlatency], fmt='o', yerr=[chosenlatencydev], color=ktocolor(chosen.kstale))
    text(chosen.tstale, chosenlatency, "%dN%dR%dW" % (result.config.N,
                                                      result.config.R, 
                                                      config.W), fontsize=8)

'''

for result in results:
    plot_with_errorbars(result)

#errorbar(0, 0, fmt='o', color="black", label="K=1")
#errorbar(0, 0, fmt='o', color="blue", label="K=2")
#legend(loc="upper right", numpoints=1)

title("N=%d, p_staler = %f" % (results.keys()[0].N, 1.0-percentile))
xlabel("t-staleness (ms)")
ylabel("average write + read latency (ms)")
savefig("latency-stale.pdf")

show()
