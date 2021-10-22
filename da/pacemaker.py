# validator_info  : consists of all the items which we  were accessing via Main.initializer
# validator_info {
#   'BlockTree': BlockTree object
#   'Safety': Safety object
# }
from Models.timeout_msg import TimeoutMsg
from Models.timeout_certificate import TimeoutCertificate
from time import gmtime, strftime

import enum
class LoggingLevel(enum.Enum):
    NOTSET=0
    DEBUG=1
    INFO=2
    WARNING=3
    ERROR=4
    CRITICAL=5


class Pacemaker:
    def __init__(self, current_round,last_round_tc,pending_timeouts,pending_timeouts_senders,faulty_validators,delta_for_pacemaker,timeout_validators, validator_info=None):
        self.validator_info = validator_info
        self.current_round = current_round#0
        self.last_round_tc = last_round_tc#None
        self.pending_timeouts = pending_timeouts#{}  # dictionary of set (key:round,value:set of tmo_info  getting timed_out) : may have to verify
        self.pending_timeouts_senders = pending_timeouts_senders#{}  # extra dictionary of set (key:round,value:set of tmo_info.senders  getting timed_out) : may have to verify
        self.faulty_validators=faulty_validators
        self.timeout_validators = timeout_validators
        self.delta_for_pacemaker=delta_for_pacemaker

    def setValidator_info(self,validator_info):
        self.validator_info = validator_info
    def get_round_timer(self, r):
        # distAlgo: set timer for a round expiry
        return self.delta_for_pacemaker*4

    def start_timer(self, new_round):
        self.stop_timer(self.current_round)
        self.current_round = new_round
        # handled in main run
        # distAlgo: start timer for this current_round for duration=get_round_timer(initializer.current_round)

    def save_consensus_state(self):
        # As per professor
        pass

    def local_timeout_round(self):
        # self.save_consensus_state() #As per professor

        timeout_info = self.validator_info["Safety"].make_timeout(self.current_round,
                                                                  self.validator_info["BlockTree"].high_qc,
                                                                  self.last_round_tc)

        timeout_message = TimeoutMsg(timeout_info, self.last_round_tc, self.validator_info["BlockTree"].high_commit_qc)
        return timeout_message

    # To Do timeout
    def process_remote_timeout(self, tmo):
        tmo_info = tmo.tmo_info
        if tmo_info.block_round < self.current_round:
            return None

        if tmo_info.block_round in self.pending_timeouts_senders:

            if tmo_info.sender not in self.pending_timeouts_senders[tmo_info.block_round]:
                self.pending_timeouts[tmo_info.block_round].add(tmo_info)
                self.pending_timeouts_senders[tmo_info.block_round].add(tmo_info.sender)
        else:
            self.pending_timeouts[tmo_info.block_round] = {tmo_info}
            self.pending_timeouts_senders[tmo_info.block_round] = {tmo_info.sender}


        if len(self.pending_timeouts_senders[tmo_info.block_round]) == self.faulty_validators + 1:
            self.stop_timer(self.current_round)
            self.local_timeout_round()

        if len(self.pending_timeouts_senders[tmo_info.block_round]) == (2 * self.faulty_validators) + 1:

            high_qc_rounds_vector = [tmo_info.high_qc.vote_info.round for tmo_info in
                                     self.pending_timeouts[tmo_info.block_round] if tmo_info.high_qc is not None  ]
            signature_list = [tmo_info.signature for tmo_info in self.pending_timeouts[tmo_info.block_round]]
            if len(self.timeout_validators) > 0:
                self.logToFile(str("Validator: " + self.validator_info["Main"]["u"] + "created Timeout Message: "),LoggingLevel.INFO)

            return TimeoutCertificate(tmo_info.block_round, high_qc_rounds_vector, signature_list)

        return None

    def advance_round_tc(self, tc):

        if tc is None or tc.block_round < self.current_round:
            return False

        self.last_round_tc = tc
        self.start_timer(tc.block_round + 1)
        return True

    def advance_round_qc(self, qc):

        if qc is None or qc.vote_info.round < self.current_round:
            return False

        self.last_round_tc = None

        self.start_timer(qc.vote_info.round + 1)
        return True

    def stop_timer(self, round):
        # handled in main run
        pass

    def logToFile(self,msg,level):
        f = open(self.validator_info["Main"]["logger_file"], "a")
        msg = "[" +level.name+"]: " +strftime("%Y-%m-%d %H:%M:%S ", gmtime())+"  \t\t "+ "[ "+ msg + " ]\n"
        f.write(msg)
        f.close()