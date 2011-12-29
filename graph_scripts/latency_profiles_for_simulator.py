from os import system, listdir
from plot_utils import *
from analytical_utils import *

#resultsfile = "../results/2011-12-02-00_11_28/"
#resultsfile = "../../ernst-cassandra/bench/results/2011-12-22-14_58_26"

results = []

#lmbdas = get_lmbdas(resultsfile)
#results_l = fetch_results(resultsfile)
#for lmbda in lmbdas:
#  for R in range(1, 4):
#    for W in range(1, 4):
#      if R+W > 4:
#        continue
#      results.append(fetch_result(resultsfile, 3, R, W, lmbda[0], lmbda[1]))

#results.sort(key=lambda result: result.config.rlmbda)

#system("rm -r analyzedir*")

for d in listdir(resultsfile):
    if d.find("N") == -1:
        continue
    for s in listdir(resultsfile+"/"+d):
        if s.find("PROXY") == -1:
            continue
        N=int(d[0])
        R=int(d[2])
        W=int(d[4])
        lmbdas = d[7:]
        lmbdas = lmbdas.split('-')
        wlmbda = lmbdas[0][2:]
        rlmbda = lmbdas[1][2:]
        resultdir = "%s/%dN%dR%dW-WL%s-AL%s-RL%s-SL%s/" % (resultsfile, N, R, W, wlmbda, rlmbda, rlmbda, rlmbda)
        id_name = "R"+str(R)+"W"+str(W)+"-"+str(rlmbda)+str(wlmbda)
        system("mkdir -p analyzedir-cd-" + id_name)
        print "config root is " + resultdir
        extract_latency_profiles(resultdir, "analyzedir-cd-" + id_name)
