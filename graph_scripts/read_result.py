
class ReadResult:
    def __init__(self,
                 version,
                 starttime,
                 endtime,
                 read_version,
                 lastcommittedversion,
                 lastcommittedtime,
                 kstale,
                 latency):
        self.version = version
        self.starttime = starttime/1000000.0
        self.endtime = endtime/1000000.0
        self.lastcommittedversion = lastcommittedversion
        self.lastcommittedtime = lastcommittedtime/1000000.0
        self.kstale = kstale
        self.latency = latency/1000000.0

