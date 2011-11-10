

from plot_utils import *
from math import ceil
from pylab import *

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
    tstales, percentiles=get_t_staleness_series(1, result)


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

    plot(tstales, percentiles, label=str(result.config.lmbda)[:5])


ax = gca()
ax.set_xscale("symlog")

title("N: %d, R: %d, W: %d" % (result.config.N, result.config.R, result.config.W))
xlabel("Time After Commit (ms)")
ylabel("pstale")

legend()

show()
        
