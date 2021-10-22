class TimeoutCertificate:
    def __init__(self, block_round=None, tmo_high_qc_rounds=None, tmo_signatures=None):
        # All messages that form TimeoutCertificate need to have the same round
        self.block_round = block_round
        # 2f + 1 high_qc round numbers of the timeout messages that form the TC
        self.tmo_high_qc_rounds = tmo_high_qc_rounds
        # 2f + 1 signatures of (round, tmo_high_qc_round) that form the TC
        self.tmo_signatures = tmo_signatures
