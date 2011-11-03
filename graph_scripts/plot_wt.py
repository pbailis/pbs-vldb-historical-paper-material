
from os import listdir
from math import ceil
from collections import defaultdict
from scipy import stats
from scipy import mean
from scipy import std
from pylab import *

def parse_results(results_dir):
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
    #print "number of keys: %d"%(len(keys))

    for num_wait in range(1, W+1):
      values = []
      for k in keys:
        end_times = wt_fin_dict[k]
        end_times.sort()
        values.append(end_times[num_wait - 1] - wt_start_dict[k])

      figure()
      plot(keys, values, '.', label='wt %d'%(num_wait)) 
      title("wt-%d for %s" %(num_wait, results_dir))
      xlabel("key")
      ylabel("wait time in ms")
      print("wait for %d, wait time median: %f, 99 pc: %f, avg: %f," \
          "std: %f" %(num_wait, stats.scoreatpercentile(values, 50), \
            stats.scoreatpercentile(values, 99), mean(values), \
              std(values))) 
      savefig("wt-%d-%d.pdf"%(W,num_wait))


parse_results("../results/micro/5N-2011-10-31-23_04_57/5N1R5W")
parse_results("../results/micro/5N-2011-10-31-23_04_57/5N1R4W")
parse_results("../results/micro/5N-2011-10-31-23_04_57/5N1R3W")
parse_results("../results/micro/5N-2011-10-31-23_04_57/5N1R2W")
parse_results("../results/micro/5N-2011-10-31-23_04_57/5N1R1W")
parse_results("../results/micro/5N-2011-10-31-23_04_57/5N2R1W")
parse_results("../results/micro/5N-2011-10-31-23_04_57/5N2R2W")
parse_results("../results/micro/5N-2011-10-31-23_04_57/5N2R3W")
parse_results("../results/micro/5N-2011-10-31-23_04_57/5N2R4W")
parse_results("../results/micro/5N-2011-10-31-23_04_57/5N3R1W")
parse_results("../results/micro/5N-2011-10-31-23_04_57/5N3R2W")
parse_results("../results/micro/5N-2011-10-31-23_04_57/5N3R3W")
parse_results("../results/micro/5N-2011-10-31-23_04_57/5N4R1W")
parse_results("../results/micro/5N-2011-10-31-23_04_57/5N4R2W")
parse_results("../results/micro/5N-2011-10-31-23_04_57/5N5R1W")
