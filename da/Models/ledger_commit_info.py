class LedgerCommitInfo:
    def __init__(self, commit_state_id=-1, vote_info_hash=""):
        # Proof of Ledger history. Can implement as the hash of the merkle tree of the Ledger history
        self.commit_state_id = commit_state_id # need to verify
        # Hash of the corresponding VoteInfo
        self.vote_info_hash = vote_info_hash #vote_info_hash need to verify
