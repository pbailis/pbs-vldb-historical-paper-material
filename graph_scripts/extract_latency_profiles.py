
from sys import argv

version_to_starttimes = {}
write_latencies = {}
read_latencies = {}
onewaywrite_latencies = {}

if(len(argv) < 4):
    print "USAGE: outdir, proxyfile, serverfile(s)"
    exit(-1)

outdir = argv[1]
proxyfile = argv[2]
serverfiles = argv[3:]

NS_PER_MS = 1000000.0

def write_out_latencies(outfile, latencies):
    f = open(outdir+"/"+outfile, 'w')
    latencysort = latencies.keys()
    latencysort.sort()
    for latency in latencysort:
        f.write("1 %d %d\n" % (latencies[latency], latency))
    f.close()

#collect write info
for line in open(proxyfile):
    if line.find("WS") != -1:

        write_start = int(line.split()[4].strip(','))/NS_PER_MS
        write_start_version = int(line.split()[5].strip(','))
        write_start_clock = int(line.split()[6])

        version_to_starttimes[write_start_version] = write_start_clock

    elif line.find("WC") != -1:
        write_end = int(line.split()[2].strip(','))/NS_PER_MS

        latency = write_end-write_start

        if latency not in write_latencies:
            write_latencies[latency] = 0
        write_latencies[latency] += 1
        
    elif line.find("RS") != -1:
        read_start = int(line.split()[4])/NS_PER_MS
    elif line.find("RC") != -1:
        read_end = int(line.split()[2])/NS_PER_MS

        latency = read_end-read_start

        if latency not in read_latencies:
            read_latencies[latency] = 0
        read_latencies[latency] += 1

for serverfile in serverfiles:
    for line in open(serverfile):
        if line.find("remote applied") != -1:
            version = int(line.split()[3])
            whenapplied = int(line.split()[7])
        
            latency = whenapplied-version_to_starttimes[version]
            
            if latency < 0:
                continue

            if latency not in onewaywrite_latencies:
                onewaywrite_latencies[latency] = 0
            onewaywrite_latencies[latency] += 1


write_out_latencies("wlatency.dist", write_latencies)
write_out_latencies("rlatency.dist", read_latencies)
write_out_latencies("onewaywrite.dist", onewaywrite_latencies)
    
