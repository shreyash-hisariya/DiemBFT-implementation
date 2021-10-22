class TimeoutInfo:
    def __init__(self, block_round, high_qc, sender, signature):
        # Round in which block was generated
        self.block_round = block_round
        # Highest known QC
        self.high_qc = high_qc
        # Sender of the timeout
        self.sender = sender
        # block_round and high_qc signed by the sender
        self.signature = signature
