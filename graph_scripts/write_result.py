
class WriteResult:
    def __init__(self,
                 value,
                 starttime,
                 endtime,
                 latency):
        self.value = value
        self.starttime = starttime/1000000.0
        self.endtime = endtime/1000000.0
        self.latency = latency/1000000.0

