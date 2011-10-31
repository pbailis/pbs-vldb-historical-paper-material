
from read_result import *
from config_settings import *
from os import listdir

NS_PER_MS = 1000000.0

def fetch_results(resultsdir):
    resultsdict = {}

    for d in listdir(resultsdir):
        if d.find("N") == -1:
            continue
        for s in listdir(resultsdir+"/"+d):
            if s.find("PROXY") == -1:
                continue
            N=int(d[0])
            R=int(d[2])
            W=int(d[4])

            resultsdict[ConfigSettings(N, R, W)] = parse_file(resultsdir+"/"+d+"/"+s+"/cassandra.log")

    return resultsdict

def order_by_t_stale(readlist):
    readlist.sort(key=lambda res: res.tstale)

def order_by_k_stale(readlist):
    readlist.sort(key=lambda res: res.kstale)

def order_by_latency(readlist):
    readlist.sort(key=lambda res: res.latency)

def parse_file(f):
    ret = []
    write_latencies = []
    version_commits = {}

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

            version_commits[last_committed_version] = write_end
            write_latencies.append((write_end-write_start)/NS_PER_MS)

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
                    #t-staleness
                    (read_start - version_commits[read_version])/NS_PER_MS,
                    #k-staleness
                    read_version - last_committed_version,
                    #latency
                    (read_end - read_start)/NS_PER_MS)

            assert res.latency > 0

            ret.append(res)

    return [ret, write_latencies]
