
class ResultsClass:
    def __init__(self,
                 config,
                 reads,
                 writes,
                 commit_times):
        self.config = config
        self.reads = reads
        self.writes = writes
        self.commit_times = commit_times
