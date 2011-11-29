

from plot_utils import *
from analytical_utils import *
from math import ceil
from pylab import *

k=1

results = []

lmbdas = get_lmbdas(resultsfile)
for lmbda in lmbdas:
    results.append(fetch_result(resultsfile, 3, 1, 1, lmbda[0], lmbda[1]))

results.sort(key=lambda result: result.config.wlmbda)

def chunkBins(seq, num):
  avg = len(seq) / float(num)
  out = []
  last = 0.0

  while last < len(seq):
    out.append(seq[int(last):int(last + avg)])
    last += avg

  return out

for result in results:
    tstales, percentiles=get_t_staleness_series(k, result)


    ''''
    timeandstale = zip(times, stales)

    
    numbins = 100

    bins = chunkBins(timeandstale, numbins)

    errorbar([average([r[0] for r in b]) for b in bins],
             [average([r[1] for r in b]) for b in bins],
             fmt='o-',
             yerr=[std([r[1] for r in b]) for b in bins],
             label = str(result.config.lmbda)[:5])

    '''

    print result.config.wlmbda, result.config.rlmbda
    
    wlatency =  average([w.latency for w in result.writes])
    rlatency = average([r.latency for r in result.reads])

    hist([w.latency for w in result.writes], 100)
    show()
    cla()

    print wlatency, rlatency

    ratio = wlatency/rlatency

    roundratio = round(ratio, 2)

    plot(tstales, percentiles, 'o-', label=str(roundratio)+","+str(wlatency))

for result in results:
    continue
    config = result.config

    times, stales = sweep_t(config.rootconfigdir, config, k)

    print times, stales
    stales = [1-stale for stale in stales]
    plot(times, stales, 'o-', label=str(result.config.wlmbda)[:5]+"A", ms=5)

ax = gca()

title("N: %d, R: %d, W: %d" % (result.config.N, result.config.R, result.config.W))
xlabel("Time After Commit (ms)")
ylabel("1-pstaler")

legend(loc="lower right", title="Write:Read Latency")

ax.set_xscale('symlog')

savefig("t-cdf.pdf")

#show()
        
