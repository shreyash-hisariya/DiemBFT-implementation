class BlockTree:
    def __init__(self, vote_info, ledger_commit_info, vote_msg, qc, block):
        # Author of the block
        self.vote_info = vote_info
        # Round in which block is generated
        self.ledger_commit_info = ledger_commit_info
        # Payload of transactions to be committed
        self.vote_msg = vote_msg
        # Quorum certificate of the parent block
        self.qc = qc
        # Digest of author, block_round, payload, quorum_cert.vote_info.id, quorum_cert.signatures
        self.block = block
