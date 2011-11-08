
class KTResult:
    def __init__(self,
                 config,
                 kstale,
                 tstale,
                 latency,
                 latencydev,
                 staler_reads,
                 current_reads,
                 pstale):
        self.config = config
        self.kstale = kstale
        self.tstale = tstale
        self.latency = latency
        self.latencydev = latencydev
        self.staler_reads = staler_reads
        self.current_reads = current_reads
        self.pstale = pstale
