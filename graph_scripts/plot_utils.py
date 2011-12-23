
from collections import defaultdict
from k_t_result import *
from results_class import *
from read_result import *
from write_result import *
from config_settings import *
from os import listdir
from pylab import *

#resultsfile = "../../ernst-cassandra/bench/results/2011-12-20-22_52_44"
#resultsfile = "../results/2011-12-19-12_44_45"
#resultsfile = "../results/2011-12-08-23_32_27"
resultsfile = "../../ernst-cassandra/bench/results/2011-12-22-14_58_26"

NS_PER_MS = 1000000.0

def get_lmbdas(resultsdir):
    ret = []
    for d in listdir(resultsdir):
        if d.find("N") == -1:
            continue
        lmbdas = d[7:]
        lmbdas = lmbdas.split('-')
        wl = lmbdas[0][2:]
        rl = lmbdas[1][2:]
        if [wl, rl] not in ret:
            ret.append([wl, rl])

    return ret

def fetch_result(resultsdir, N, R, W, wlmbda, rlmbda):
    resultdir = "%s/%dN%dR%dW-WL%s-AL%s-RL%s-SL%s/" % (resultsdir, N, R, W, wlmbda, rlmbda, rlmbda, rlmbda)
    for s in listdir(resultdir):
        if s.find("PROXY") != -1:
            proxy = s

    config = ConfigSettings(N, R, W, wlmbda, rlmbda, resultdir)
    return parse_file(config, resultdir+proxy+"/cassandra.log")

def fetch_results(resultsdir):
    ret = []

    for d in listdir(resultsdir):
        if d.find("N") == -1:
            continue
        for s in listdir(resultsdir+"/"+d):
            if s.find("PROXY") == -1:
                continue
            N=int(d[0])
            R=int(d[2])
            W=int(d[4])
            lmbdas = d[7:]
            lmbdas = lmbdas.split('-')
            wlmbda = lmbdas[0][2:]
            rlmbda = lmbdas[1][2:]
            resultdir = "%s/%dN%dR%dW-WL%s-AL%s-RL%s-SL%s/" % (resultsdir, N, R, W, wlmbda, rlmbda, rlmbda, rlmbda)

            config = ConfigSettings(N, R, W, wlmbda, rlmbda, resultdir)
            
            yield(parse_file(config, resultsdir+"/"+d+"/"+s+"/cassandra.log"))

'''
def order_by_t_stale(readlist):
    readlist.sort(key=lambda res: res.tstale)

def order_by_k_stale(readlist):
    readlist.sort(key=lambda res: res.kstale)

def order_by_latency(readlist):
    readlist.sort(key=lambda res: res.latency)
'''

def parse_file(config, f):
    reads = []
    writes = []
    commit_times = {}

    #collect write info
    for line in open(f):
        if line.find("WS") != -1:
            write_start = int(line.split()[4].strip(','))/NS_PER_MS
            write_start_version = int(line.split()[5].strip(','))
            write_start_clock = int(line.split()[6].strip(','))
        elif line.find("WC") != -1:
            write_end = int(line.split()[2].strip(','))/NS_PER_MS
            last_committed_version = int(line.split()[3].strip(','))
            write_end_clock = int(line.split()[4].strip(','))

            assert last_committed_version == write_start_version

            #if (write_end_clock <= write_start_clock):
              #print str(write_start_clock) + " " + str(write_end_clock) + " " + str(write_start_version) + " " + str(last_committed_version)
              #continue
            assert write_end-write_start

            commit_times[last_committed_version] = write_end_clock
            writes.append(WriteResult(write_start_version,
                                      write_start,
                                      write_end,
                                      write_end-write_start,
                                      write_start_clock,
                                      write_end_clock))

    writes.sort(key=lambda w: w.endtime)

    #then collect read info; reads can come back before write commits!
    write_commit_index = -1

    print "working with file %s" % (f)
    for line in open(f):
        if line.find("WC") != -1:
            write_commit_index += 1
        elif line.find("RS") != -1:
            read_start = int(line.split()[4])/NS_PER_MS
            read_start_clock = int(line.split()[5])

            #find the corresponding write

            search_index = write_commit_index
            while True:
              if search_index != -1:
                if search_index == len(writes)-1 or writes[search_index].endtime > read_start:
                    break
              search_index += 1

            while True:
                if writes[search_index].endtime < read_start:
                    last_write = writes[search_index]
                    break
                if search_index == 0:
                    break
                search_index -= 1

            # Read was before any write
            if search_index == 0:
                last_committed_version_at_read_start = -1
                last_committed_version_time_at_read_start = -1
            else:
                last_committed_version_at_read_start = last_write.version
                last_committed_version_time_at_read_start = last_write.endtime
                assert read_start >= last_committed_version_time_at_read_start

            if search_index != 0 and search_index != len(writes)-1:
                assert read_start-writes[search_index].endtime > 0
                assert read_start-writes[search_index+1].endtime < 0

        elif line.find("RC") != -1:
            read_end = int(line.split()[2])/NS_PER_MS
            read_version = int(line.split()[3])
            read_end_clock = int(line.split()[4])

            if config.R + config.W > config.N:
                assert read_version >= last_committed_version_at_read_start

            # Ignore read that happened before any write
            if last_committed_version_at_read_start != -1:
              res = ReadResult(
                      #read version
                      read_version,
                      #start time
                      read_start,
                      #end time
                      read_end,
                      #read version
                      read_version,
                      #last commited version,
                      last_committed_version_at_read_start,
                      #last commit time
                      last_committed_version_time_at_read_start,
                      #k-staleness
                      read_version - last_committed_version_at_read_start,
                      #latency
                      (read_end - read_start),
                      #read start clock time
                      read_)

              assert res.latency > 0

              reads.append(res)

    return ResultsClass(config, reads, writes, commit_times)

def get_latency_staleness_results(k, result, percentile):

    assert k >= 1

    result.reads.sort(key=lambda read: read.starttime-
                      read.last_committed_time_at_read_start)
    
    staler = 0
    #current w.r.t. k
    current = 0

    result.reads.reverse()

    prev_freshness = 1
    tstale = 0

    how_many_stale = ceil(len(result.reads)*(1-percentile))


    #compute the probability of staleness at each t
    for read in result.reads:
        if read.version >= read.last_committed_version_at_read_start-(k-1):
            #if read.version-read.last_committed_version_at_read_start-(k-1) < 0:
            #print k, read.version-read.last_committed_version_at_read_start-(k-1)
            current += 1
        else:
            staler += 1

        if(staler > how_many_stale and tstale == 0):
            tstale = read.starttime-read.last_committed_time_at_read_start


    print how_many_stale, staler, len(result.reads)


    latency = (average([r.latency for r in result.reads])
               + average([w.latency for w in result.writes]))
    #standard error on the mean
    latencydev = (sqrt(pow(std([r.latency for r in result.reads])/sqrt(len(result.reads)), 2)+
                      pow(std([w.latency for w in result.writes])/sqrt(len(result.writes)), 2)))

    return KTResult(result.config, k, tstale, latency, latencydev, staler, current, 1-prev_freshness)


def get_t_staleness_series(k, result):
    assert k >= 1

    result.reads.sort(key=lambda read: read.starttime-
                      read.last_committed_time_at_read_start)

    result.reads.reverse()
    
    percentiles = []
    tstales = []

    for percentile in xrange(900, 1000, 1):
        tstale=0
        staler = 0
        #current w.r.t. k
        current = 0

        how_many_stale = ceil(len(result.reads)*(1-percentile/1000.0))

    #compute the probability of staleness at each t
        for read in result.reads:
            if read.version >= read.last_committed_version_at_read_start-(k-1):
                current += 1
            else:
                staler += 1

            if(staler > how_many_stale):
                tstale = read.starttime-read.last_committed_time_at_read_start
                break

        print how_many_stale, staler, len(result.reads)
        tstales.append(tstale)
        percentiles.append(percentile/1000.0)

    return tstales, percentiles

def round_to(n, precision):
  correction = 0.5 if n >= 0 else -0.5
  return int(n/precision+correction)*precision

# Works only for k = 0 right now
def get_t_staleness_windows(result):
    # Sort the writes by start time
    result.writes.sort(key=lambda write: write.starttime)
    #result.reads.sort(key=lambda read: read.starttime-
    #                  read.last_committed_time_at_read_start)

    # Array counting number of stales
    stales = defaultdict(int) #[0]*1200
    currents = defaultdict(int) #[0]*1200
    total_reads = 0
    
    print "num writes " + str(len(result.writes))
    print "num reads " + str(len(result.reads))
    for r in result.reads:
      # read for this write
      is_stale = (r.version < r.last_committed_version_at_read_start)
      #print "is_stale " + str(is_stale)
      timestep = int(math.ceil(r.starttime - r.last_committed_time_at_read_start))
      if timestep >= 600:
        #print "r.starttime %d r.last_committed_time_at_read_start %d r.version %d r.last_committed_version_at_read_start %d" % (r.starttime, r.last_committed_time_at_read_start, r.version, r.last_committed_version_at_read_start) 
        continue
      if is_stale:
        stales[timestep] = stales[timestep] + 1
        total_reads = total_reads + 1
      else:
        currents[timestep] = currents[timestep] + 1
        total_reads = total_reads + 1
    
    percentiles = []
    tstales = []
    stales_count = []
    #for t in xrange(0, 600, 1):
    for t in sorted(stales.iterkeys()):
      if ((stales[t] + currents[t]) >= 100):
        #print "t:%d stales:%d currents: %d, p %f" % (t, stales[t], currents[t], 1-(float(stales[t])/float(stales[t]+currents[t])) )
        tstales.append(t)
        percentiles.append(1-(float(stales[t])/float(stales[t]+currents[t])))
        stales_count.append(stales[t])

    return tstales, percentiles, stales_count 

def plot_cdf(results, fmt, lbl, color):

    vals = []
    freqs = []

    results.sort()

    prev = -1
    for i in range(0, len(results)):
        if results[i] == prev:
            continue
        else:
            print prev, (i-1)/float(len(results))
            if prev != -1:
                vals.append(prev)
                freqs.append((i-1)/float(len(results)))
            prev = results[i]

    plot(vals, freqs, fmt, label=lbl, color = color)
