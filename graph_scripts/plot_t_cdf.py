

from plot_utils import *
from analytical_utils import *
from math import ceil
from pylab import *

k=1

results = []

lmbdas = get_lmbdas(resultsfile)
for lmbda in lmbdas:
    results.append(fetch_result(resultsfile, 3, 1, 1, lmbda))

results.sort(key=lambda result: result.config.lmbda)

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

    print result.config.lmbda

    plot(tstales, percentiles, 'o-', label=str(result.config.lmbda)[:5])

for result in results:
    config = result.config
    '''
    print config.lmbda
    if float(config.lmbda) == .002:
        times, stales = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900], [0.895129, 0.924491, 0.946839, 0.963284, 0.975073, 0.983337, 0.988995, 0.992792, 0.995309, 0.996961]
    elif float(config.lmbda) == .005:
        times, stales= [0, 100, 200, 300, 400, 500, 600, 700, 800, 900], [0.903216, 0.959166, 0.98458, 0.994605, 0.998155, 0.999346, 0.999756, 0.999913, 0.999977, 0.999998]
    else:
        continue
    '''
    times, stales = sweep_t(config.rootconfigdir, config, k)

    print times, stales
    stales = [1-stale for stale in stales]
    plot(times, stales, 'o-', label=str(result.config.lmbda)[:5]+"A", ms=5)

ax = gca()

title("N: %d, R: %d, W: %d" % (result.config.N, result.config.R, result.config.W))
xlabel("Time After Commit (ms)")
ylabel("pstale")

legend()

show()
        
