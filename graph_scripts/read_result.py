
class ReadResult:
    def __init__(self,
                 value,
                 starttime,
                 endtime,
                 read_version,
                 lastcommittime,
                 kstale,
                 latency):
        self.value = value
        self.starttime = starttime
        self.endtime = endtime
        self.lastcommittime = lastcommittime
        self.kstale = kstale
        self.latency = latency

