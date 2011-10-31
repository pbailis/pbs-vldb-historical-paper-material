
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

def plot_with_errorbars(config, results):
    #results[config][0] is ReadResults
    #results[config][1] is writelatencies
    chosen = results[config][0][pctile_index]
    chosenlatency = average([r.latency for r in results[config][0][:pctile_index]])+average([latency for latency in results[config][1]])
    chosenlatencydev = sqrt(pow(std([r.latency for r in results[config][0][:pctile_index]]), 2)+
                            pow(std([latency for latency in results[config][1]]), 2))

    errorbar([chosen.tstale], [chosenlatency], fmt='o', yerr=[chosenlatencydev], color=ktocolor(chosen.kstale))
    text(chosen.tstale+.02, chosenlatency, "%dN%dR%dW" % (config.N, config.R, config.W), fontsize=8)

for config in results:
    print len(results[config][0])
    pctile_index = int(ceil(len(results[config][0])*percentile))

    ### nth percentile by t-staleness
    order_by_t_stale(results[config][0])
    #plot_with_errorbars(config, results)

    ### nth percentile by version
    order_by_k_stale(results[config][0])
    #plot_with_errorbars(config, results)

    ### nth percentile by latency
    order_by_latency(results[config][0])
    plot_with_errorbars(config, results)


errorbar(-10000, 0, fmt='o', color="black", label="K=1")
errorbar(-10000, 0, fmt='o', color="blue", label="K=2")
legend(loc="upper right", numpoints=1)

xlim(xmin=0, xmax=150)

title("N=%d, p_staler = %f" % (results.keys()[0].N, 1.0-percentile))
xlabel("t-staleness (ms)")
ylabel("average write + read latency (ms)")
savefig("latency-stale.pdf")

show()
