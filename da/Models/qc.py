class QC:
    def __init__(self, vote_info, ledger_commit_info, signatures, author, author_signature):
        # VoteInfo record of the QC
        self.vote_info = vote_info
        # Speculated Ledger commit info if the block is committed
        self.ledger_commit_info = ledger_commit_info
        # Quorum of signatures
        self.signatures = signatures # has to be made list
        # Validator that produced the QC
        self.author = author
        # the signatures signed by the author of the QC
        self.author_signature = author_signature
