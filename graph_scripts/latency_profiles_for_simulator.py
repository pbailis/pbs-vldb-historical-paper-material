from os import system, listdir
from plot_utils import *
from analytical_utils import *

resultsfile = "../results/2011-11-11-14_57_02/"

results = []

lmbdas = get_lmbdas(resultsfile)
for lmbda in lmbdas:
    results.append(fetch_result(resultsfile, 3, 1, 1, lmbda))

results.sort(key=lambda result: result.config.lmbda)


system("rm -r analyzedir*")

for result in results:
    config = result.config
    system("mkdir -p analyzedir-" + str(result.config.lmbda))
    extract_latency_profiles(config.rootconfigdir, "analyzedir-" + str(result.config.lmbda))
