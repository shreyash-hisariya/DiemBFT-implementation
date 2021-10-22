class Block:
    def __init__(self, author, block_round, payload, quorum_cert, block_id):
        # Author of the block
        self.author = author
        # Round in which block is generated
        self.round = block_round
        # Payload of transactions to be committed
        self.payload = payload
        # Quorum certificate of the parent block
        self.qc = quorum_cert
        # Digest of author, block_round, payload, quorum_cert.vote_info.id, quorum_cert.signatures
        self.id = block_id
