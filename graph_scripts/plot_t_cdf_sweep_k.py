

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

for result in results:
    if float(result.config.wlmbda) != .05:
        continue
    for k in range(1, 5):
        tstales, percentiles=get_t_staleness_series(k, result)


        plot(tstales, percentiles, 'o-', label=str(k))

for result in results:
    continue
    config = result.config

    times, stales = sweep_t(config.rootconfigdir, config, k)

    print times, stales
    stales = [1-stale for stale in stales]
    plot(times, stales, 'o-', label=str(result.config.wlmbda)[:5]+"A", ms=5)

ax = gca()

ax.set_xscale('symlog')

title("N: %d, R: %d, W: %d, W Lambda: %s R Lambda: %s" % (result.config.N, result.config.R, result.config.W, result.config.wlmbda, result.config.rlmbda))
xlabel("Time After Commit (ms)")
ylabel("1-pstaler")

legend(loc="lower right", title="k")

savefig("t-cdf-k.pdf")

#show()
        
