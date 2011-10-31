
from results_class import *
from read_result import *
from write_result import *
from config_settings import *
from os import listdir

NS_PER_MS = 1000000.0

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

            config = ConfigSettings(N, R, W)
            
            ret.append(parse_file(config, resultsdir+"/"+d+"/"+s+"/cassandra.log"))

    return ret

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
            write_start = int(line.split()[4].strip(','))
            write_start_version = int(line.split()[5].strip(','))
        elif line.find("WC") != -1:
            write_end = int(line.split()[4].strip(','))
            last_committed_version = int(line.split()[5].strip(','))

            assert last_committed_version == write_start_version
            assert write_end-write_start

            commit_times[last_committed_version] = write_end
            writes.append(WriteResult(write_start_version,
                                      write_start,
                                      write_end,
                                      write_end-write_start))

    #then collect read info; reads can come back before write commits!
    for line in open(f):
        if line.find("WS") != -1:
            write_start = int(line.split()[4].strip(','))
            write_start_version = int(line.split()[5].strip(','))
        elif line.find("WC") != -1:
            write_end = int(line.split()[4].strip(','))
            last_committed_version = int(line.split()[5].strip(','))
        elif line.find("RS") != -1:
            read_start = int(line.split()[4])
        elif line.find("RC") != -1:
            read_end = int(line.split()[4])
            read_version = int(line.split()[5])

            res = ReadResult(
                    #value
                    read_version,
                    #start time
                    read_start,
                    #end time
                    read_end,
                    #read version
                    read_version,
                    #last commit time
                    write_end,
                    #k-staleness
                    read_version - last_committed_version,
                    #latency
                    (read_end - read_start)/NS_PER_MS)

            assert res.latency > 0

            reads.append(res)

    return ResultsClass(config, reads, writes, commit_times)
