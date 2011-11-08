
from plot_utils import *
from math import ceil, log
from pylab import *
from random import *

results = fetch_results(resultsfile)

percentile = .99

def get_nth_percentile(l, pctile):
    return l[int(ceil(pctile*len(l)))]

for result in results:
    write_latencies = [write.latency for write in result.writes]
    write_latencies.sort()

    read_latencies = [read.latency for read in result.reads]
    read_latencies.sort()

    print ("N: %d R: %d W: %d lambda %f\nAvg write latency: %f (stddev: %f, 99th %%ile: %f)\nAvg read latency: %f (stddev: %f, 99th %%ile: %f)\n" %
    (result.config.N, 
     result.config.R,
     result.config.W,
     result.config.lmbda,
     average([write_latencies]),
     std(write_latencies),
     get_nth_percentile(write_latencies, percentile),
     average([read_latencies]),
     std(read_latencies),
     get_nth_percentile(read_latencies, percentile)))

    hist([4+expovariate(result.config.lmbda) for i in range(0, len(result.reads))], 100, label="expected")
    hist([read.latency for read in result.reads], 100, label="observedreads")
    hist([read.latency for read in result.writes], 100, label="observedwrites")

    legend()

    #show()
