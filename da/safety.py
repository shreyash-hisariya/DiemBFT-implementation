# validator_info  : consists of all the items which we  were accessing via Main.initializer
# validator_info {
#   'Main' : {main variables}
#   'BlockTree': Block_tree object
# }

from Models.vote_info import VoteInfo
from Models.ledger_commit_info import LedgerCommitInfo
from Models.vote_msg import VoteMsg
from Models.timeout_info import TimeoutInfo
from time import gmtime, strftime

import enum
class LoggingLevel(enum.Enum):
    NOTSET=0
    DEBUG=1
    INFO=2
    WARNING=3
    ERROR=4
    CRITICAL=5


class Safety:
    def __init__(self, private_key,public_keys,highest_vote_round,highest_qc_round,qc_round,validator_info=None):
        self.validator_info = validator_info
        self.private_key = private_key#'private_keys'
        self.public_keys = public_keys#'public_keys'
        self.highest_vote_round =highest_vote_round# -1
        self.highest_qc_round = highest_qc_round#-1
        self.qc_round = qc_round # -1

    def setValidator_info(self,validator_info):
        self.validator_info = validator_info

    def valid_signatures(self, high_qc, last_tc):
        return True

    def _increase_highest_vote_round(self, round):

        self.highest_vote_round = max(round, self.highest_vote_round)

    def _update_highest_qc_round(self, qc_round):
        self.highest_qc_round = max(qc_round, self.highest_qc_round)

    def _consecutive(self, block_round, qc_round):
        return (qc_round + 1) == block_round

    def _safe_to_extend(self, block_round, qc_round, tc):
        if tc is None:
            return True
        return self._consecutive(block_round, tc.block_round) and qc_round >= max(tc.tmo_high_qc_rounds)

    def _safe_to_vote(self, block_round, qc_round, tc):

        if block_round <= max(self.highest_vote_round, qc_round):
            return False
        return self._consecutive(block_round, qc_round) or self._safe_to_extend(block_round, qc_round, tc)

    def _safe_to_timeout(self, round, qc_round, tc):
        if qc_round < self.highest_vote_round or round <= max(self.highest_vote_round - 1, qc_round):
            return False

        if tc is None:
            return self._consecutive(round, qc_round)
        return self._consecutive(round, qc_round) or self._consecutive(round, tc.round) # handle tc none

    def _commit_state_id_candidate(self, block_round, qc):
        if qc is None:
            return -1  # need to verify
        elif self._consecutive(block_round, qc.vote_info.round):
            return self.validator_info["Ledger"].pending_state(qc.vote_info.id)  # need to verify
        else:
            return None

    def hash_func(self, a="", b="", c="", d="", e=""):
        return hash(str(a) + str(e) + str(b) + str(c) + str(d))

    def make_vote(self, b, last_tc):

        if b.qc is None:
            self.qc_round = -1
        else:
            self.qc_round = b.qc.vote_info.round


        if self.valid_signatures(b, last_tc) and self._safe_to_vote(b.round, self.qc_round, last_tc):

            self._update_highest_qc_round(self.qc_round)
            self._increase_highest_vote_round(b.round)

            if b.qc is None:
                vote_info = VoteInfo(b.id, b.round, -1, self.qc_round,
                                     self.validator_info["Ledger"].pending_state(b.id))
                hash_vote_info = self.hash_func(b.id, b.round, -1, self.qc_round,
                                                self.validator_info["Ledger"].pending_state(b.id))
            else:

                vote_info = VoteInfo(b.id, b.round, b.qc.vote_info.id, self.qc_round,
                                     self.validator_info["Ledger"].pending_state(b.id))

                hash_vote_info = self.hash_func(b.id, b.round, b.qc.vote_info.id, self.qc_round,
                                                self.validator_info["Ledger"].pending_state(b.id))


            if b.qc is not None:

                ledger_commit_info = LedgerCommitInfo(self._commit_state_id_candidate(b.round, b.qc),
                                                      hash_vote_info)
            else:
                ledger_commit_info = LedgerCommitInfo(self._commit_state_id_candidate(b.round, None), hash_vote_info)


            signature = self.private_key.sign(str(str(ledger_commit_info.commit_state_id)+str(ledger_commit_info.vote_info_hash)).encode('utf-8'))
            self.logToFile(str("Validator: " + self.validator_info["Main"]["u"] + "created Votemsg : "),LoggingLevel.INFO)

            return VoteMsg(vote_info, ledger_commit_info, self.validator_info["BlockTree"].high_commit_qc,
                           self.validator_info["Main"]["u"], signature)
        return None

    def make_timeout(self, round, high_qc, last_tc):

        if high_qc is None:
            self.qc_round = -1
            high_qc_sign = 'None'
        else:
            self.qc_round = high_qc.vote_info.round
            high_qc_sign = str(high_qc.vote_info.round)

        if self.valid_signatures(high_qc, last_tc) and self._safe_to_timeout(round, self.qc_round, last_tc):

            self._increase_highest_vote_round(round)
            signature = self.validator_info["Main"]["signature_dict"]["private_key"].sign(str(str(round) + high_qc_sign).encode('utf-8'))

            return TimeoutInfo(round, high_qc, self.validator_info["Main"]["u"], signature)
        return None

    def logToFile(self,msg, level):
        f = open(self.validator_info["Main"]["logger_file"], "a")
        msg = "[" + level.name + "]: " + strftime("%Y-%m-%d %H:%M:%S ", gmtime()) + "  \t\t " + "[ " + msg + " ]\n"
        f.write(msg)
        f.close()