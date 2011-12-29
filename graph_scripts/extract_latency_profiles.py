
from sys import argv
from os import environ
import collections

version_to_writestarttimes = {}
version_to_writeendtimes = {}
version_to_write_finish = collections.defaultdict(dict)

read_version_to_end = collections.defaultdict(lambda: collections.defaultdict(list))
read_version_to_start = collections.defaultdict(lambda: collections.defaultdict(list))
count = 0

write_latencies = {}
read_latencies = {}

onewaywrite_latencies = {}
onewayack_latencies = {}
onewayread_latencies = {}
onewayresponse_latencies = {}

clock_diffs = {}

HOME_DIR=environ['HOME']
R_CLUSTER_FILE="/.rcluster-instances"

ZERO_VERS="/tmp/0-versions"
ZERO_READ_START="/tmp/0-read-start"

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

#zero_vers = {}
#for line in open(ZERO_VERS):
#  zero_vers[int(line)] = 1 

#zero_read_start = {}
#for line in open(ZERO_READ_START):
#  zero_read_start[int(line)] = 1 

#collect write info
for line in open(proxyfile):
    if line.find("WS") != -1:

        write_start = int(line.split()[4].strip(','))/NS_PER_MS
        write_start_version = int(line.split()[5].strip(','))
        write_start_clock = int(line.split()[6])

        version_to_writestarttimes[write_start_version] = write_start_clock

    elif line.find("WC") != -1:
        write_end = int(line.split()[2].strip(','))/NS_PER_MS
        write_end_version = int(line.split()[3].strip(','))
        write_end_clock = int(line.split()[4])

        latency = write_end_clock-write_start_clock

        if latency not in write_latencies:
            write_latencies[latency] = 0
        write_latencies[latency] += 1

        version_to_writeendtimes[write_start_version] = write_end_clock
    elif line.find("finished write (post-delay)") != -1:
    #elif line.find("finished wait (post-delay)") != -1:
        wait_end_clock = int(line.split()[10].strip(','))
        wait_end_version = int(line.split()[3].strip(','))
        wait_finish_host = line.split()[4]
        version_to_write_finish[wait_end_version][wait_finish_host] = wait_end_clock
    elif line.find("finished read (post-delay)") != -1:
        read_start_time = int(line.split()[11])
        read_msg_host = line.split()[4]
        read_end_time = int(line.split()[10])
        version = int(line.split()[3])
        read_version_to_start[read_msg_host][version].append(read_start_time)
        read_version_to_end[read_msg_host][version].append(read_end_time)
        count = count + 1

    elif line.find("RS") != -1:
        read_start = int(line.split()[4])/NS_PER_MS
        read_start_clock = int(line.split()[5])
    elif line.find("RC") != -1:
        read_end = int(line.split()[2])/NS_PER_MS
        read_end_clock = int(line.split()[4])
        read_version = int(line.split()[3])

        latency = read_end_clock-read_start_clock

        if latency not in read_latencies:
            read_latencies[latency] = 0
        read_latencies[latency] += 1

print("num oneway reads = " + str(count))

#zero_ws = collections.defaultdict(list)
#zero_as = collections.defaultdict(list)

server_state = get_ec2_state()
for serverfile in serverfiles:
    servername = get_server_name(serverfile)
    ip = get_internal_ip(servername, server_state)
    read_host = "/"+ip
    start_list = read_version_to_start[read_host]
    end_list = read_version_to_end[read_host]
    version_list_pos = collections.defaultdict(int)
    for line in open(serverfile):
        if line.find("remote applied") != -1:
            version = int(line.split()[3])

            whenapplied = int(line.split()[7])
            #whenapplied = int(whenapplied - clock_diffs[servername])
        
            latency = whenapplied-version_to_writestarttimes[version]
            
            if latency < 0:
                #print "W servername start, end, when were " + servername + " " + \
                #    str(version_to_writestarttimes[version]) + " " + \
                #    str(version_to_writeendtimes[version]) + " " + \
                #    str(whenapplied)
                continue

            if latency not in onewaywrite_latencies:
                onewaywrite_latencies[latency] = 0

            #if version in zero_vers:
            onewaywrite_latencies[latency] += 1

            if read_host not in version_to_write_finish[version]:
              print "ip " + str(ip) + " missing in " + str(version)
              continue
            latency = version_to_write_finish[version]["/"+ip]-whenapplied
            
            if latency < 0:
                 #rint "servername start, end, when were " + servername + " "+  \
                 #   str(version_to_writestarttimes[version]) + " " + \
                 #   str(version_to_write_finish[version]["/"+ip]) + " " + \
                 #   str(whenapplied) + " " + str(version)
                continue
            
          
            if latency not in onewayack_latencies:
                onewayack_latencies[latency] = 0
            
            #if version in zero_vers:
            onewayack_latencies[latency] += 1

            #write_latency = version_to_writeendtimes[version]-version_to_writestarttimes[version]-latency

            #if write_latency not in write_latencies:
            #    write_latencies[write_latency] = 0
            #write_latencies[latency] += 1
        elif line.find("remote read") != -1:
            version = int(line.split()[3])
            list_pos = version_list_pos[version]
            if len(start_list[version]) <= list_pos:
              continue
            if len(end_list[version]) <= list_pos:
              continue

            read_start_time = start_list[version][list_pos]
            read_end_time = end_list[version][list_pos]
            version_list_pos[version] += 1

            whenapplied = int(line.split()[7])
            onewaylatency = whenapplied - read_start_time

            if onewaylatency < 0:
              #print "servername start, end, when were " + servername + " "+  \
              #    str(read_start_time) + " " + \
              #    str(read_end_time) + " " + \
              #    str(whenapplied)
              continue

            if onewaylatency not in onewayread_latencies:
                onewayread_latencies[onewaylatency] = 0

            #if read_start_time in zero_read_start:
            onewayread_latencies[onewaylatency] += 1

            onewaylatency = read_end_time - whenapplied
            if onewaylatency == -1:
              onewaylatency = 0
            if onewaylatency < 0:
              #print "servername start, end, when were " + servername + " "+  \
              #    str(read_start_time) + " " + \
              #    str(read_end_time) + " " + \
              #    str(whenapplied)
              continue
          
            if onewaylatency not in onewayresponse_latencies:
                onewayresponse_latencies[onewaylatency] = 0
            
            #if read_start_time in zero_read_start:
            onewayresponse_latencies[onewaylatency] += 1

print "num in write_latencies " + str(sum(write_latencies.values()))
print "num in read_latencies " + str(sum(read_latencies.values()))
print "num in oneway_write_latencies " + str(sum(onewaywrite_latencies.values()))
print "num in oneway_ack_latencies " + str(sum(onewayack_latencies.values()))
print "num in oneway_read_latencies " + str(sum(onewayread_latencies.values()))
print "num in oneway_response_latencies " + str(sum(onewayresponse_latencies.values()))

write_out_latencies("wlatency.dist", write_latencies)
write_out_latencies("rlatency.dist", read_latencies)
write_out_latencies("onewaywrite.dist", onewaywrite_latencies)
write_out_latencies("onewayack.dist", onewayack_latencies)
write_out_latencies("onewayread.dist", onewayread_latencies)
write_out_latencies("onewayresponse.dist", onewayresponse_latencies)

#for z in zero_read_start:
#  ver = zero_read_vers[z]
#  if (len(zero_ws[ver]) != len(zero_rs[z])):
#    print "length mismatch ignoring %d %d" % (len(zero_ws[ver]), len(zero_rs[z]))
#    continue
#  print "%d " % (ver),
#  print "%d " % (z),
#  for i in xrange(0, len(zero_ws[ver])):
#    print "%d " % (zero_ws[ver][i]),
#    print "%d " % (zero_rs[z][i]+zero_ss[z][i]),

#  print "\n",

#for z in sorted(zero_vers.iterkeys()):
#  print "%d " % (z),
#  print "%d " % (version_to_writestarttimes[z]),
#  for i in xrange(0, len(zero_ws[z])):
#    print "%d %d " % (zero_ws[z][i], zero_as[z][i]),
#  print "\n",
