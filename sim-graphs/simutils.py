
from os import system

def run_sim(N, R, W, k, iters, config, simsettings, outfile):
    print "java -jar dynamosim.jar %d %d %d %d %d %s O %s > %s" % (N, R, W,k, iters, config, simsettings, outfile)
    system("java -jar dynamosim.jar %d %d %d %d %d %s O %s > %s" % (N, R, W, k, iters, config, simsettings, outfile))

