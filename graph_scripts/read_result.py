
class ReadResult:
    def __init__(self,
                 version,
                 starttime,
                 endtime,
                 read_version,
                 lastcommittedversionatreadstart,
                 lastcommittedtimeatreadstart,
                 kstale,
                 latency,
                 startclock,
                 endclock,
                 lastcommittedclockatreadstart):
        self.version = version
        self.starttime = starttime
        self.endtime = endtime
        self.last_committed_version_at_read_start = lastcommittedversionatreadstart
        self.last_committed_time_at_read_start = lastcommittedtimeatreadstart
        self.kstale = kstale
        self.latency = latency
        self.startclock = startclock
        self.endclock = endclock
        self.last_committed_clock_at_read_start = lastcommittedclockatreadstart
        
        assert starttime >= lastcommittedtimeatreadstart
