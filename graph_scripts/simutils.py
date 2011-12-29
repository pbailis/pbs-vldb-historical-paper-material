from os import system

def run_sim_settings(N, R, W, k, iters, writespacing, readsperwrite,
    send_latency_file, ack_latency_file, read_latency_file,
    response_latency_file, outfile, simsettings):
    print "java -cp dynamosim.jar ernst.simulator.Simulator %d %d %d %d %d %d %d FILE %s %s %s %s O %s > %s" % (N, R, W,k, iters, writespacing, readsperwrite, send_latency_file, ack_latency_file, read_latency_file, response_latency_file, simsettings, outfile)
    system("java -cp dynamosim.jar ernst.simulator.Simulator  %d %d %d %d %d %d %d FILE %s %s %s %s O %s > %s" % (N, R, W, k, iters, writespacing, readsperwrite, send_latency_file, ack_latency_file, read_latency_file, response_latency_file, simsettings, outfile))
    #print "java -cp dynamosim.jar ernst.simulator.Simulator %d %d %d %d %d %d %d EXPONENTIAL %f %f O %s > %s" % (N, R, W,k, iters, writespacing, readsperwrite, 0.2, 0.5, simsettings, outfile)
    #system("java -cp dynamosim.jar ernst.simulator.Simulator  %d %d %d %d %d %d %d EXPONENTIAL %f %f O %s > %s" % (N, R, W, k, iters, writespacing, readsperwrite, 0.2, 0.5, simsettings, outfile))

def run_sim_lat(N, R, W, k, iters, writespacing, readsperwrite,
    send_latency_file, ack_latency_file, read_latency_file,
    response_latency_file, outfile):
    simsettings="LATSCDF" 
    run_sim_settings(N, R, W, k, iters, writespacing, readsperwrite, send_latency_file, ack_latency_file, read_latency_file, response_latency_file, outfile, simsettings)

def run_sim(N, R, W, k, iters, writespacing, readsperwrite,
    send_latency_file, ack_latency_file, read_latency_file,
    response_latency_file, outfile):
    simsettings="SWEEP" 
    run_sim_settings(N, R, W, k, iters, writespacing, readsperwrite, send_latency_file, ack_latency_file, read_latency_file, response_latency_file, outfile, simsettings)
