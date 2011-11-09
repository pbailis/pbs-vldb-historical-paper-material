
from os import listdir
from math import ceil
from collections import defaultdict
#from scipy import stats
#from scipy import mean
#from scipy import std
from pylab import *

# write_latencies is keyed by W.
# each dictionary within it is keyed by latency ciel in ms 
write_latencies = defaultdict(lambda: defaultdict(int))

def parse_results_dir(results_dir):
  W = int(results_dir.split("/")[4][4])
  R = int(results_dir.split("/")[4][2])
  N = int(results_dir.split("/")[4][0])
  print "R %d W %d"%(R,W)
  for s in listdir(results_dir):
    if s.find("PROXY") == -1:
      continue
    wt_start_dict = {}
    # Key is timestamp and value is list of times observed for this key
    wt_fin_dict = defaultdict(list)

    filename = results_dir+"/"+s+"/system.log"
    #print "using file %s"%(filename)
    for line in open(filename):
      if line.find("WS") != -1:
        key = int(line.split()[10].strip(','))
        start = int(line.split()[11].strip(','))
        wt_start_dict[key] = start
      elif line.find("finished") != -1:
        key = int(line.split()[8].strip(','))
        fin = int(line.split()[12].strip(','))
        wt_fin_dict[key].append(fin)

    keys = wt_start_dict.keys()
    keys.sort()
    for k in keys:
      wt_fin_dict[k].sort()
    #print "number of keys: %d"%(len(keys))

    for num_wait in range(1, W+1):
      values = []
      for k in keys:
        end_times = wt_fin_dict[k]
        latency = end_times[num_wait - 1] - wt_start_dict[k]
        values.append(latency)
        latency_bucket = int(ceil(latency))
        if latency < 0: 
          print "Latency is %d for num_wait %d, key %d, start %d" \
              %(latency, num_wait, k, wt_start_dict[k])
          latency_bucket = 0

        write_latencies[num_wait][latency_bucket] = \
          write_latencies[num_wait][latency_bucket] + 1

      #figure()
      #plot(keys, values, '.', label='wt %d'%(num_wait)) 
      #title("wt-%d for %s" %(num_wait, results_dir))
      #xlabel("key")
      #ylabel("wait time in ms")
      #print("wait for %d, wait time median: %f, 99 pc: %f, avg: %f," \
      #   "std: %f" %(num_wait, stats.scoreatpercentile(values, 50), \
      #      stats.scoreatpercentile(values, 99), mean(values), \
      #        std(values))) 
      #savefig("wt-%d-%d.pdf"%(W,num_wait))


def all_results(results_root):
  for d in listdir(results_root):
    if d.find("N") == -1:
      continue
    parse_results_dir(results_root+"/"+d)

#all_results("../results/micro/5N-2011-11-03-23_11_46")
all_results("../results/2011-11-08-10_50_43/")

for k in write_latencies.keys():
  for j in write_latencies[k].keys():
    print "%d %d %d" % (k, j, write_latencies[k][j])
