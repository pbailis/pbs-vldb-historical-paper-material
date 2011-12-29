
from os import system
from plot_utils import *
from analytical_utils import *
from simutils import *
from math import ceil
from pylab import *
from bisect import *

k=0
iters=3000000
writespacing=200
readsperwrite=5000

results = []
rmses = []
nrmses = []

# Extract latency profiles first
#system("python ./latency_profiles_for_simulator.py")
#exit(0)

lmbdas = get_lmbdas(resultsfile)
results = fetch_results(resultsfile)
#for lmbda in lmbdas:
#  for R in range(1, 3):
#    for W in range(1, 3):
#      if R+W > 4:
#        continue
#      results.append(fetch_result(resultsfile, 3, R, W, lmbda[0], lmbda[1]))

#results.sort(key=lambda result: result.config.wlmbda)

def stdev(inputs):
  sum_inputs = 0
  sumsq_inputs = 0
  for i in inputs:
    sum_inputs += i 
    sumsq_inputs += i*i 
  return math.sqrt(sumsq_inputs/len(inputs) - pow(sum_inputs/len(inputs), 2))

def find_ge(a, key):
    '''Find smallest item greater-than or equal to key.
    Raise ValueError if no such item exists.
    If multiple keys are equal, return the leftmost.

    '''
    i = bisect_left(a, key)
    if i == len(a):
        raise ValueError('No item found with key at or above: %r' % (key,))
    return a[i], i


#cla()
for result in results:
    print result.config.wlmbda, result.config.rlmbda
    id_name = "R"+str(result.config.R)+"W"+str(result.config.W)+"-"+str(result.config.rlmbda)+str(result.config.wlmbda)

    obs_write_latencies_map = {}
    obs_read_latencies_map = {}

    wsum = 0
    rsum = 0
    # Open wlatencies file
    for line in open("analyzedir-cd-"+id_name+"/wlatency.dist"):
      wsum = wsum + int(line.split()[2])
    print "wsum is " + str(wsum)
    for line in open("analyzedir-cd-"+id_name+"/rlatency.dist"):
      rsum = rsum + int(line.split()[2])

    wrunning_sum = 0
    for line in open("analyzedir-cd-"+id_name+"/wlatency.dist"):
      wrunning_sum += float(line.split()[2])
      obs_write_latencies_map[wrunning_sum / float(wsum)] = float(line.split()[1])
    
    running_sum = 0
    for line in open("analyzedir-cd-"+id_name+"/rlatency.dist"):
      running_sum += float(line.split()[2])
      obs_read_latencies_map[running_sum / float(rsum)] = float(line.split()[1])
    
    owv = [obs_write_latencies_map[kv] for kv in sorted(obs_write_latencies_map.keys())]
    orv = [obs_read_latencies_map[kv] for kv in sorted(obs_read_latencies_map.keys())]

    plot(owv, sorted(obs_write_latencies_map.keys()), '^-',
        label="observed-write")
    plot(orv, sorted(obs_read_latencies_map.keys()), 'o-',
        label="observed-read")

    # Run simulator for this config
    run_sim_lat(result.config.N, result.config.R, result.config.W, k, iters,
        writespacing, readsperwrite,
        "analyzedir-cd-"+id_name+"/onewaywrite.dist",
        "analyzedir-cd-"+id_name+"/onewayack.dist",
        "analyzedir-cd-"+id_name+"/onewayread.dist", 
        "analyzedir-cd-"+id_name+"/onewayresponse.dist", "sim-latencies-"+id_name)
    # Parse simulator results, calculate RMSE etc.
    
    write_latencies_map = {}
    read_latencies_map = {}

    mode = ""
    for line in open("sim-latencies-"+id_name):
      if line.find("WRITE") != -1:
        mode = "write"
      elif line.find("READ") != -1:
        mode = "read"
      else:
        percentile = float(line.split()[0])
        latency = float(line.split()[1]) 
        if mode is "write":
          write_latencies_map[percentile] = latency
        elif mode is "read":
          read_latencies_map[percentile] = latency

    wv = [write_latencies_map[kv] for kv in sorted(write_latencies_map.keys())]
    rv = [read_latencies_map[kv] for kv in sorted(read_latencies_map.keys())]
    plot(wv, sorted(write_latencies_map.keys()), 'D-', label=str("write-sim"))
    plot(rv, sorted(read_latencies_map.keys()), 's-',
        label=str("read-sim"))
    
    sum_sq = 0
    for p in xrange(0, 1000, 1):
      val,ind = find_ge(sorted(read_latencies_map.keys()), float(p)/1000.0)
      oval,oind = find_ge(sorted(obs_read_latencies_map.keys()), float(p)/1000.0)
      obs = obs_read_latencies_map[oval]
      exp = read_latencies_map[val]
      #print str(p) + " " + str(obs) + " " + str(exp)
      sum_sq = sum_sq + pow(( obs - exp ), 2)
      
    rmse = math.sqrt(sum_sq / len(xrange(0,1000,1)))
    nrmse = rmse * 100 / (max(obs_read_latencies_map.values()) - min(obs_read_latencies_map.values()))
    rmses.append(rmse)
    nrmses.append(nrmse)
    print "Read latency RMSE " + id_name + " is " + str(rmse) + " NRMSE is " + str(nrmse)

    sum_sq = 0
    for p in xrange(0, 1000, 1):
      val,ind = find_ge(sorted(write_latencies_map.keys()), float(p)/1000.0)
      oval,oind = find_ge(sorted(obs_write_latencies_map.keys()), float(p)/1000.0)
      obs = obs_write_latencies_map[oval]
      exp = write_latencies_map[val]
      #print str(p) + " " + str(obs) + " " + str(exp)
      sum_sq = sum_sq + pow(( obs - exp ), 2)
      
    rmse = math.sqrt(sum_sq / len(xrange(0,1000,1)))
    nrmse = rmse * 100 / (max(obs_write_latencies_map.values()) - min(obs_write_latencies_map.values()))
    rmses.append(rmse)
    nrmses.append(nrmse)
    print "Write latency RMSE " + id_name + " is " + str(rmse) + " NRMSE is " + str(nrmse)

    # Calculate RMSE
    #sum_sq = 0
    #for i in xrange(0, len(tstales), 1):
    #  if tstales[i] in t_map:
    #    print i, tstales[i], percentiles[i], t_map[tstales[i]], stales[i]
    #    obs = percentiles[i]
    #    exp = t_map[tstales[i]]
    #    sum_sq = sum_sq + pow((obs - exp), 2)
 
    #rmse = math.sqrt(sum_sq / len(tstales))
    #print "RMSE " + id_name + " is " + str(rmse)

ax = gca()

#title("N: %d, R: %d, W: %d" % (result.config.N, result.config.R, result.config.W))
xlabel("Latency")
ylabel("cdf")

legend(loc="lower right", title="Simulator-Comparison")

ax.set_xscale('symlog')

savefig("latency-cdf.pdf")

print "Mean RMSE " + str(math.fsum(rmses)/len(rmses))
print "Max RMSE " + str(max(rmses))
print "Std. dev RMSE " + str(stdev(rmses))

print "Mean NRMSE " + str(math.fsum(nrmses)/len(nrmses))
print "Max NRMSE " + str(max(nrmses))
print "Std. dev NRMSE " + str(stdev(nrmses))

#show()
