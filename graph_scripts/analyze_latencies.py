
from plot_utils import *
from math import ceil
from pylab import *

results = fetch_results("../results/micro/5N-2011-31-23_04_57")

percentile = .99

def get_nth_percentile(l, pctile):
    return l[int(ceil(pctile*len(l)))]

for result in results:
    write_latencies = [write.latency for write in result.writes]
    write_latencies.sort()

    read_latencies = [read.latency for read in result.reads]
    read_latencies.sort()

    print ("N: %d R: %d W: %d\nAvg write latency: %f (stddev: %f, 99th %%ile: %f)\nAvg read latency: %f (stddev: %f, 99th %%ile: %f)\n" %
    (result.config.N, 
     result.config.R,
     result.config.W,
     average([write_latencies]),
     std(write_latencies),
     get_nth_percentile(write_latencies, percentile),
     average([read_latencies]),
     std(read_latencies),
     get_nth_percentile(read_latencies, percentile)))
