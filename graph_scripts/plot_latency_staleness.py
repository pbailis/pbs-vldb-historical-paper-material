
from plot_utils import *
from math import ceil
from pylab import *

results = fetch_results("../results/micro/5N-2011-31-23_04_57")

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
            staler += 1
            
        pstale_at_t[read.starttime-read.last_committed_time_at_read_start] = float(staler)/(staler+current)

    #find the t such that p_staler < percentile for all T >= t
    times = pstale_at_t.keys()
    times.sort()
    times.reverse()

    chosen = -1

    if max(pstale_at_t.values()) <= 1-percentile:
        chosen = 0
    else:
        for t in range(0, len(times)):

            #this is on the reversed array, so if pstale_at_t(T) is <= 1-percentile,
            #then all t > t are also <= 1-percentile
            if (pstale_at_t[times[t]] <= 1-percentile 
                and pstale_at_t[times[t+1]] > 1-percentile):
                chosen = times[t]
                break

    latency = (average([r.latency for r in result.reads])
               + average([w.latency for w in result.writes]))
    latencydev = sqrt(pow(std([r.latency for r in result.reads]), 2)+
                      pow(std([w.latency for w in result.writes]), 2))

    print "%dR %dW\n%d within %d versions, %d staler %d total" % (result.config.R, result.config.W, current, k, staler, current+staler)
    print "DID R%d W%d" % (result.config.R, result.config.W)
    errorbar(chosen, latency, fmt='o-', yerr=latencydev)
    text(chosen, latency, "%dN%dR%dW" % (result.config.N,
                                         result.config.R, 
                                         result.config.W), fontsize=8)


for result in results:
    #plot_with_errorbars(1, result)
    hist([write.latency for write in result.writes], 100, label="%dR%dW" % (result.config.R, result.config.W))

    N = result.config.N

legend()

#errorbar(0, 0, fmt='o', color="black", label="K=1")
#errorbar(0, 0, fmt='o', color="blue", label="K=2")
#legend(loc="upper right", numpoints=1)

title("N=%d, p_staler = %f" % (N, 1.0-percentile))
xlim(xmax=100)
xlabel("t-staleness (ms)")
ylabel("average write + read latency (ms)")
savefig("latency-stale.pdf")

show()
