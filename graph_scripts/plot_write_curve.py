

from plot_utils import *
from analytical_utils import *
from math import ceil
from pylab import *
from random import random

k=1

results = []

lambda_to_color={.002:"brown",
                  .005:"blue",
                  .010:"green",
                  .05:"red",
                  .1:"black"}

def gen_gamma_exponential(many, lmbda):
    ret = []

    for i in range(0, many):
        trials = []
        for trial in range(0, 3):
            trials.append(log(1-random())/(-lmbda)+log(1-random())/(-lmbda))

        ret.append(min(trials))
    return ret


lmbdas = get_lmbdas(resultsfile)

for lmbda in lmbdas:
    results.append(fetch_result(resultsfile, 3, 1, 1, lmbda))

results.sort(key=lambda result: result.config.lmbda)

for result in results:
    config = result.config
    lats  = get_latencies(config.rootconfigdir, "wlatency.dist", config, k)

    plot_cdf(lats, '-', result.config.lmbda, lambda_to_color[float(config.lmbda)])
    #plot_cdf(gen_gamma_exponential(len(lats), float(config.lmbda)), "--", "expected "+result.config.lmbda, lambda_to_color[float(config.lmbda)])
    ax = gca()

    title("N: %d, R: %d, W: %d" % (result.config.N, result.config.R, result.config.W))
    xlabel("Write Latency (ms)")
    ylabel("Cumulative Density")
    legend(loc="lower right", title="Lambda")


ax.set_xscale('log')

savefig("write-cdf.pdf")
        
