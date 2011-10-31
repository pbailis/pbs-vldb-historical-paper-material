
from read_result import *
from config_settings import *
from os import listdir

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
            print N, R, W

            resultsdict[ConfigSettings(N, R, W)] = parse_file(resultsdir+"/"+d+"/"+s+"/cassandra.log")

    return resultsdict

def parse_file(f):
    ret = []
    version_commits = {}

    #collect write info
    for line in open(f):
        if line.find("WS") != -1:
            write_start = int(line.split()[4].strip(','))
            write_start_version = int(line.split()[5].strip(','))
        elif line.find("WC") != -1:
            write_end = int(line.split()[4].strip(','))
            last_committed_version = int(line.split()[5].strip(','))

            version_commits[last_committed_version] = write_end
            assert last_committed_version == write_start_version

    #then collect read info; reads can come back before write commits!
    for line in open(f):
        if line.find("RS") != -1:
            read_start = int(line.split()[4])
        elif line.find("RC") != -1:
            read_end = int(line.split()[4])
            read_version = int(line.split()[5])

            res = ReadResult(
                    #value
                    read_version,
                    #k-staleness
                    last_committed_version - read_version,
                    #t-staleness
                    read_end - version_commits[read_version],
                    #latency
                    read_end - read_start)

            assert res.latency > 0

            ret.append(res)

    return ret
