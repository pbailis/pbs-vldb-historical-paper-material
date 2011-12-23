
class WriteResult:
    def __init__(self,
                 version,
                 starttime,
                 endtime,
                 latency,
                 startclock,
                 endclock):
        self.version = version
        self.starttime = starttime
        self.endtime = endtime
        self.latency = latency
        self.startclock = startclock
        self.endclock = endclock

