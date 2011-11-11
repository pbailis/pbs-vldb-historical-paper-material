
from os import system

solverconfig = "\n \
n=%d\n \
wmin=%d\n \
p_s=%f\n \
t-stale=%f\n \
k-stale=%d\n \
c_r=%f\n \
c_w=%f\n \
 \
\#unused for optimize \
r=%d\n \
\#optimize, sweep_t, or calc_staleness, sweep_r_w_t_fixed_k \
actiontype=%s\n \
r-latency-model=%s\n \
w-latency-model=%s\n \
oneway-latency-model=%s\n"

simdir = "../nrw_solver"

def run_solver(outfile):
    system(simdir+"/bin/runsolver analyzedir/analyze.conf" + " > "+outfile)

def extract_latency_profiles(resultsdir, outdir):
    for f in os.listdir(resultsdir):
        servers = []
        if f.find("PROXY") != -1:
            proxy = f
        elif f.find("ec2") != -1:
            servers.append(server)
    
    extractcmd = "python extract_latency_profiles.py "+outdir+" "+proxy

    for slave in servers:
        extractcmd += " " + slave

    system(extractcmd)

def set_up_configfile(outfile, n, w, ps, t, k, cr, cw, r, actiontype, rmodel, wmodel, writewaymodel):
    f = open(outfile, 'w')
    f.write(solverconfig % (n, w, ps, t, k, cr, cw, r, actiontype, rmodel, wmodel, writewaymodel))
    f.close()

def set_up_solver(resultsdir, config, ps, t, k, cr, cw, actiontype):
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
    ret = []
    for line in open(resultsfile):
        print line
    return ret

def sweep_t(resultsdir, config):
    set_up_solver(resultdir, config, 
                  #ps unused
                  0,
                  #t, k unused,
                  0, k,
                  #cr, cw unused
                  .5, .5,
                  "sweep_t")
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
