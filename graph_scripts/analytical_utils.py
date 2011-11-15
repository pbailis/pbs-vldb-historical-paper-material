
from os import system, listdir

solverconfig = "\n \
n=%d\n \
wmin=%d\n \
p_s=%f\n \
t-stale=%f\n \
k-stale=%d\n \
c_r=%f\n \
c_w=%f\n \
 \
#unused for optimize \n \
r=%d\n \
#optimize, sweep_t, or calc_staleness, sweep_r_w_t_fixed_k \n \
actiontype=%s\n \
r-latency-model=%s\n \
w-latency-model=%s\n \
oneway-latency-model=%s\n"

simdir = "../nrw_solver/"

def run_solver(outfile):
    system("java -jar "+simdir+"build/nrwsolver.jar analyzedir/analyze.conf" + " > "+outfile)

def extract_latency_profiles(resultsdir, outdir):
    servers = []

    for f in listdir(resultsdir):
        if f.find("PROXY") != -1:
            proxy = f
        elif f.find("ec2") != -1:
            servers.append(f)
    
    extractcmd = "python extract_latency_profiles.py "+outdir+" "+resultsdir+"/"+proxy+"/cassandra.log"

    for slave in servers:
        extractcmd = extractcmd+" "+resultsdir+"/"+ slave+"/cassandra.log"

    system(extractcmd)

def set_up_configfile(outfile, n, w, ps, t, k, cr, cw, r, actiontype, rmodel, wmodel, writewaymodel):
    f = open(outfile, 'w')
    f.write(solverconfig % (n, w, ps, t, k, cr, cw, r, actiontype, rmodel, wmodel, writewaymodel))
    f.close()

def set_up_solver(resultsdir, config, ps, t, k, cr, cw, actiontype):
    system("rm -r analyzedir")
    system("mkdir analyzedir")
    extract_latency_profiles(resultsdir, "analyzedir")
    set_up_configfile("analyzedir/analyze.conf", config.N,
                     config.W,
                     ps,
                     t,
                     k,
                     cr,
                     cw,
                     config.R,
                     actiontype,
                     "analyzedir/rlatency.dist",
                     "analyzedir/wlatency.dist",
                     "analyzedir/onewaywrite.dist")

def clean_up_solver():
    system("rm -rf analyzedir")

def parse_t_stale(resultsfile):
    times = []
    probs = []
    for line in open(resultsfile):
        times.append(int(line.split(',')[0]))
        probs.append(float(line.split()[1]))
    return times, probs

def get_latencies(resultsdir, dist, config, k):
    set_up_solver(resultsdir, config, 
                  #ps unused
                  0,
                  #t, k unused,
                  0, k,
                  #cr, cw unused
                  .5, .5,
                  "sweep_t")
    lats = []
    for line in open("analyzedir/"+dist):
        line = line.split()
        for i in range(0, int(line[2])):
            lats.append(int(float(line[1])))

    return lats

    
def sweep_t(resultsdir, config, k):
    set_up_solver(resultsdir, config, 
                  #ps unused
                  0,
                  #t, k unused,
                  0, k,
                  #cr, cw unused
                  .5, .5,
                  "sweep_t")
    print "SET UP"
    run_solver("analyzedir/sweep.out")
    return parse_t_stale("analyzedir/sweep.out")
           
def parse_staleness(resultsfile):
    ret = []
    for line in open(resultsfile):
        print line
    return ret
     
def calc_staleness(resultsdir, config, k, cr, cw):
    set_up_solver(resultdir, config, 
                  #ps unused
                  0,
                  #t,unused,
                  0,
                  k,
                  cr,
                  cw,
                  "calc_staleness")
    run_solver("analyzedir/stale.out")
    return parse_staleness("analyzedir/stale.out")


def parse_sweep_r_w_t_fixed_k(resultsfile):
    ret = []
    for line in open(resultsfile):
        print line
    return ret
     
def sweep_r_w_t_fixed_k(resultsdir, config, ps, k, cr, cw):
    set_up_solver(resultdir, config, 
                  ps,
                  #t,unused,
                  0,
                  k,
                  cr,
                  cw,
                  "sweep_r_w_t_fixed_k")
    run_solver("analyzedir/rwsweep.out")
    return parse_sweep_r_w_t_fixed_k("analyzedir/rwsweep.out")
