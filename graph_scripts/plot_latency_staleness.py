
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

def plot_with_errorbars(k, result):
    result.reads.sort(key=lambda read: read.starttime-
                      read.last_committed_time_at_read_start)
    
    staler = 0
    #current w.r.t. k
    current = 0

    pstale_at_t = {}

    #compute the probability of staleness at each t
    for read in result.reads:
        if read.version >= read.last_committed_version_at_read_start-(k-1):
            current += 1
        else:
            print "STALE"
            staler += 1
            
        pstale_at_t[read.starttime-read.last_committed_time_at_read_start] = float(staler)/(staler+current)

    #find the t such that p_staler < percentile for all T >= t
    times = pstale_at_t.keys()
    times.sort()
    times.reverse()

    chosen = -1

    if max(pstale_at_t.values()) == 0:
        print "NO STALENESS"
        chosen = 0
    else:
        for t in range(0, len(times)):

            print times[t], pstale_at_t[times[t]]

            #this is on the reversed array, so if pstale_at_t(T) is <= 1-percentile,
            #then all t > t are also <= 1-percentile
            if (pstale_at_t[times[t]] <= 1-percentile 
                and pstale_at_t[times[t+1]] > 1-percentile):
                chosen = times[t]
                break

    print result.config.R, result.config.W, chosen

    latency = (average([r.latency for r in result.reads])
               + average([w.latency for w in result.writes]))
    latencydev = sqrt(pow(std([r.latency for r in result.reads]), 2)+
                      pow(std([w.latency for w in result.writes]), 2))

    print "DID R%d W%d" % (result.config.R, result.config.W)
    errorbar(chosen, latency, fmt='o-', yerr=latencydev)
    text(chosen, latency, "%dN%dR%dW" % (result.config.N,
                                         result.config.R, 
                                         result.config.W), fontsize=8)


for result in results:
    plot_with_errorbars(1, result)

#errorbar(0, 0, fmt='o', color="black", label="K=1")
#errorbar(0, 0, fmt='o', color="blue", label="K=2")
#legend(loc="upper right", numpoints=1)

title("N=%d, p_staler = %f" % (results[0].config.N, 1.0-percentile))
xlabel("t-staleness (ms)")
ylabel("average write + read latency (ms)")
savefig("latency-stale.pdf")

show()
