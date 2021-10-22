class TimeoutMsg:
    def __init__(self, timeout_info, last_round_tc, high_commit_qc):
        # TimeoutInfo
        self.tmo_info = timeout_info
        # TC for last round if nothing was committed in the last round, else None
        self.last_round_tc = last_round_tc
        # QC of the highest known committed transaction to the Ledger
        self.high_commit_qc = high_commit_qc
