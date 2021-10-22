class VoteInfo:
    def __init__(self, id, round, parent_id, parent_round, exec_state_id):
        # ID and round number for the corresponding block
        self.id = id
        self.round = round
        # ID and round number of the parent to the corresponding block
        self.parent_id = parent_id
        self.parent_round = parent_round
        # Speculated execution state
        self.exec_state_id = exec_state_id
