
class ReadResult:
    def __init__(self, value, tstale, kstale, latency):
        self.value = value
        self.tstale = tstale
        self.kstale = kstale
        self.latency = latency
