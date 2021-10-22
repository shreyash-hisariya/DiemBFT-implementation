class VoteMsg:
    def __init__(self, vote_info, ledger_commit_info, high_commit_qc, sender, signature):
        # Information related to the block being voted on
        self.vote_info = vote_info
        # Speculated committed Ledger state, identified by commit_state_id
        self.ledger_commit_info = ledger_commit_info
        # Highest qc that serves as a commit certificate
        self.high_commit_qc = high_commit_qc
        # Sender of the vote message
        self.sender = sender
        # ledger_commit_info signed by the sender of the message
        self.signature = signature
