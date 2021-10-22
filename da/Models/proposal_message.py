class ProposalMessage:
    def __init__(self, block, last_round_tc, high_commit_qc,signature):
        # Block that is being proposed to be committed to the Ledger
        self.block = block
        # Timeout certificate of the previous round if there was no QC committed in that round
        self.last_round_tc = last_round_tc
        # QC of the highest committed round for synchronization
        self.high_commit_qc = high_commit_qc
        self.signature=signature # current validator who is proposing
