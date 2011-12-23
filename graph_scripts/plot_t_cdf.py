
from os import system
from plot_utils import *
from analytical_utils import *
from simutils import *
from math import ceil
from pylab import *

k=0
iters=50000
writespacing=300
readsperwrite=5000

results = []

# Extract latency profiles first
#system("python ./latency_profiles_for_simulator.py")

lmbdas = get_lmbdas(resultsfile)
results = fetch_results(resultsfile)
#for lmbda in lmbdas:
#  for R in range(1, 3):
#    for W in range(1, 3):
#      if R+W > 4:
#        continue
#      results.append(fetch_result(resultsfile, 3, R, W, lmbda[0], lmbda[1]))

#results.sort(key=lambda result: result.config.wlmbda)

def chunkBins(seq, num):
  avg = len(seq) / float(num)
  out = []
  last = 0.0

  while last < len(seq):
    out.append(seq[int(last):int(last + avg)])
    last += avg

  return out

#cla()
for result in results:
    print len(result.reads)
    tstales, percentiles,stales=get_t_staleness_windows(result)
    print result.config.wlmbda, result.config.rlmbda
    id_name = "R"+str(result.config.R)+"W"+str(result.config.W)+"-"+str(result.config.rlmbda)+str(result.config.wlmbda)

    plot(tstales, percentiles, 'o-', label="R="+str(result.config.R)+",W="+str(result.config.W))
#
    # Run simulator for this config
    run_sim(result.config.N, result.config.R, result.config.W, k, iters, writespacing, readsperwrite, "analyzedir-cd-"+id_name+"/onewaywrite.dist", "analyzedir-cd-"+id_name+"/onewayack.dist", "sim-results-"+id_name)
    # Parse simulator results, calculate RMSE etc.
    
    t = []
    stale = []
    t_map = {}
    for line in open("sim-results-"+id_name):
      line = line.split()    
      t.append(float(line[1]))
      t_map[float(line[1])] = float(line[0])
      stale.append(float(line[0]))
 
    plot(t, stale, 's-', label=str("sim"), color="red")
 
    # Calculate RMSE
    sum_sq = 0
    for i in xrange(0, len(tstales), 1):
      if tstales[i] in t_map:
        print i, tstales[i], percentiles[i], t_map[tstales[i]], stales[i]
        obs = percentiles[i]
        exp = t_map[tstales[i]]
        sum_sq = sum_sq + pow((obs - exp), 2)
 
    rmse = math.sqrt(sum_sq / len(tstales))
    print "RMSE " + id_name + " is " + str(rmse)

ax = gca()

#title("N: %d, R: %d, W: %d" % (result.config.N, result.config.R, result.config.W))
xlabel("Time After Commit (ms)")
ylabel("1-pstaler")

#legend(loc="lower right", title="Simulator-Comparison")

ax.set_xscale('symlog')

savefig("t-cdf.pdf")

#show()
        
