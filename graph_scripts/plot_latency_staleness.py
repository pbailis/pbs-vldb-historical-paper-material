
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
    result.reads.sort(key=lambda read: read.starttime-read.lastcommittedtime)
    

    #k=1 consistency
    mint = -1

    times = []
    latencies = []
    latencydevs = []

    for t in range(0, 150):
        chosenreads = []
        
        latest_read = 0
        older_read = 0

        for read in result.reads:
            if read.starttime-read.lastcommittedtime > t:
                continue

            chosenreads.append(read)

            if read.version >= read.lastcommittedversion:
                latest_read += 1
            else:
                older_read += 1


        #ensure at least 100 samples
        if latest_read/float(latest_read+older_read) > percentile and latest_read+older_read > 100:
            latency = (average([r.latency for r in chosenreads])
                       + average([w.latency for w in result.writes]))
            latencydev = sqrt(pow(std([r.latency for r in result.reads]), 2)+
                              pow(std([w.latency for w in result.writes]), 2))

            times.append(t)
            latencies.append(latency)
            latencydevs.append(latencydev)
            
            print latest_read+older_read
            
            break;

    print "DID R%d W%d" % (result.config.R, result.config.W)
    errorbar(times, latencies, fmt='o-', yerr=latencydevs)
    text(times[0], latencies[0], "%dN%dR%dW" % (result.config.N,
                                                      result.config.R, 
                                                      result.config.W), fontsize=8)

for result in results:
    plot_with_errorbars(result)

#errorbar(0, 0, fmt='o', color="black", label="K=1")
#errorbar(0, 0, fmt='o', color="blue", label="K=2")
#legend(loc="upper right", numpoints=1)

title("N=%d, p_staler = %f" % (results[0].config.N, 1.0-percentile))
xlabel("t-staleness (ms)")
ylabel("average write + read latency (ms)")
savefig("latency-stale.pdf")

show()
