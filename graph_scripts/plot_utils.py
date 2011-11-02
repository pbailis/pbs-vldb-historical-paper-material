
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
            write_start = int(line.split()[4].strip(','))/1000000.0
            write_start_version = int(line.split()[5].strip(','))
        elif line.find("WC") != -1:
            write_end = int(line.split()[4].strip(','))/1000000.0
            last_committed_version = int(line.split()[5].strip(','))

            assert last_committed_version == write_start_version
            assert write_end-write_start

            commit_times[last_committed_version] = write_end
            writes.append(WriteResult(write_start_version,
                                      write_start,
                                      write_end,
                                      write_end-write_start))

    writes.sort(key=lambda w: w.endtime)

    #then collect read info; reads can come back before write commits!
    write_commit_index = -1

    for line in open(f):
        if line.find("WC") != -1:
            write_commit_index += 1
        elif line.find("RS") != -1:
            read_start = int(line.split()[4])/1000000.0

            #find the corresponding write

            search_index = write_commit_index
            while True:
                if search_index == len(writes)-1 or writes[search_index].endtime > read_start:
                    break
                search_index += 1

            while True:
                if writes[search_index].endtime < read_start:
                    last_write = writes[search_index]
                    break
                search_index -= 1


            last_committed_version_at_read_start = last_write.version
            last_committed_version_time_at_read_start = last_write.endtime

        elif line.find("RC") != -1:
            read_end = int(line.split()[4])/1000000.0
            read_version = int(line.split()[5])

            if config.R+config.W > config.N:
                assert read_version >= last_committed_version_at_read_start

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
                    (read_end - read_start)/NS_PER_MS)

            assert res.latency > 0

            reads.append(res)

    return ResultsClass(config, reads, writes, commit_times)
