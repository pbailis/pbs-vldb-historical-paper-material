
from sys import argv
from os import environ
import collections

version_to_starttimes = {}
version_to_endtimes = {}
version_to_write_finish = collections.defaultdict(dict)
write_latencies = {}
read_latencies = {}
onewaywrite_latencies = {}
onewayack_latencies = {}
clock_diffs = {}

HOME_DIR=environ['HOME']
R_CLUSTER_FILE="/.rcluster-instances"

if(len(argv) < 5):
    print "USAGE: outdir, proxyfile, clock_diff_file, serverfile(s)"
    exit(-1)

outdir = argv[1]
proxyfile = argv[2]
clockdiff_file = argv[3]
serverfiles = argv[4:]

NS_PER_MS = 1000000.0

def write_out_latencies(outfile, latencies):
    f = open(outdir+"/"+outfile, 'w')
    latencysort = latencies.keys()
    latencysort.sort()
    for latency in latencysort:
        f.write("1 %f %d\n" % (latency, latencies[latency]))
    f.close()

#build clock diff
#for line in open(clockdiff_file):
#  clock_diffs[line.split()[2]] = float(line.split()[3])

def get_servers():
    ret = []
    for line in open(HOME_DIR+R_CLUSTER_FILE):
        ret.append(line.split()[2])
    return ret

def get_internal_ip(server, ec2_state):
    return ec2_state[server]

def log_params(resultsdir, N, NUM_SERVERS, writems, readms, readers, totalwrites):
    system("mkdir -p "+resultsdir)
    f = open(resultsdir+"params.txt" , 'w')
    f.write("Servers: %d\nN: %d\nWriteMS: %d\nReadMS: %d\n Number of readers: %d\nTotal writes: %d\n" %
             (NUM_SERVERS, N, writems, readms, readers, totalwrites))
    f.close()

def get_ec2_state():
    ret = {}
    for line in open(HOME_DIR+R_CLUSTER_FILE):
        ret[line.split()[2]] = line.split()[3]

    return ret

def get_server_name(filename):
  l = len(filename.split('/'))
  return filename.split('/')[l - 2]

#collect write info
for line in open(proxyfile):
    if line.find("WS") != -1:

        write_start = int(line.split()[4].strip(','))/NS_PER_MS
        write_start_version = int(line.split()[5].strip(','))
        write_start_clock = int(line.split()[6])

        version_to_starttimes[write_start_version] = write_start_clock

    elif line.find("WC") != -1:
        write_end = int(line.split()[2].strip(','))/NS_PER_MS
        write_end_version = int(line.split()[3].strip(','))
        write_end_clock = int(line.split()[4])

        latency = write_end_clock-write_start_clock

        if latency not in write_latencies:
            write_latencies[latency] = 0
        write_latencies[latency] += 1

        version_to_endtimes[write_start_version] = write_end_clock
    elif line.find("finished wait") != -1:
        wait_end_clock = int(line.split()[10].strip(','))
        wait_end_version = int(line.split()[3].strip(','))
        wait_finish_host = line.split()[4]
        version_to_write_finish[wait_end_version][wait_finish_host] = wait_end_clock

    elif line.find("RS") != -1:
        read_start = int(line.split()[4])/NS_PER_MS
    elif line.find("RC") != -1:
        read_end = int(line.split()[2])/NS_PER_MS

        latency = read_end-read_start

        if latency not in read_latencies:
            read_latencies[latency] = 0
        read_latencies[latency] += 1

server_state = get_ec2_state()
for serverfile in serverfiles:
    servername = get_server_name(serverfile)
    ip = get_internal_ip(servername, server_state)
    for line in open(serverfile):
        if line.find("remote applied") != -1:
            version = int(line.split()[3])

            whenapplied = int(line.split()[7])
            #whenapplied = int(whenapplied - clock_diffs[servername])
        
            latency = whenapplied-version_to_starttimes[version]
            
            if latency < 0:
                #print "servername start, end, when were " + servername + " " + \
                #    str(version_to_starttimes[version]) + " " + \
                #    str(version_to_endtimes[version]) + " " + \
                #    str(whenapplied)
                continue

            if latency not in onewaywrite_latencies:
                onewaywrite_latencies[latency] = 0
            onewaywrite_latencies[latency] += 1

            latency = version_to_write_finish[version]["/"+ip]-whenapplied
            
            if latency < 0:
                print "servername start, end, when were " + servername + " "+  \
                    str(version_to_starttimes[version]) + " " + \
                    str(version_to_write_finish[version][servername]) + " " + \
                    str(whenapplied) + " " + str(version)
                continue

            if latency not in onewayack_latencies:
                onewayack_latencies[latency] = 0
            onewayack_latencies[latency] += 1

            #write_latency = version_to_endtimes[version]-version_to_starttimes[version]-latency

            #if write_latency not in write_latencies:
            #    write_latencies[write_latency] = 0
            #write_latencies[latency] += 1

print "num in write_latencies " + str(sum(write_latencies.values()))
print "num in read_latencies " + str(sum(read_latencies.values()))
print "num in oneway_write_latencies " + str(sum(onewaywrite_latencies.values()))
print "num in oneway_ack_latencies " + str(sum(onewayack_latencies.values()))

write_out_latencies("wlatency.dist", write_latencies)
write_out_latencies("rlatency.dist", read_latencies)
write_out_latencies("onewaywrite.dist", onewaywrite_latencies)
write_out_latencies("onewayack.dist", onewayack_latencies)
