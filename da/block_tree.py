from Models.block import Block
from Models.qc import QC
from nacl.signing import VerifyKey
from time import gmtime, strftime

import enum


class LoggingLevel(enum.Enum):
    NOTSET = 0
    DEBUG = 1
    INFO = 2
    WARNING = 3
    ERROR = 4
    CRITICAL = 5


# validator_info  : consists of all the items which we  were accessing via Main.initializer
# validator_info {
#       'Main' : {main variables}
#       'Ledger': ledger object
# }

class Block_tree:

    def __init__(self, pending_block_tree, pending_votes, high_qc, high_commit_qc, faulty_validators,
                 validator_info=None):
        self.validator_info = validator_info
        self.pending_block_tree = pending_block_tree  # []  # may need to verify => change this to dict key:blockid value block
        self.pending_votes = pending_votes  # {}  # dictionary where key is hash(v.ledger_commit_info) and value is set of signatures
        self.high_qc = high_qc  # None
        self.high_commit_qc = high_commit_qc  # None
        self.faulty_validators = faulty_validators

    def setValidator_info(self, validator_info):
        self.validator_info = validator_info

    def getMaxRound(self, qc, high_commit_qc, update_high_commit_qc):

        if qc is not None:
            if self.high_qc is not None and update_high_commit_qc == True:
                self.high_commit_qc = self.high_qc
            elif update_high_commit_qc == False:
                self.high_qc = qc

    def process_qc(self, qc):

        if qc is not None:

            signatures_list = qc.signatures
            if self.verifySignature(qc.author, qc.author_signature,
                                    self.generateSignRecur(signatures_list).encode('utf-8')) == False:
                return False

        if qc is not None and qc.ledger_commit_info.commit_state_id != -1:
            self.validator_info["Ledger"].commit(qc.vote_info.parent_id)
            self.prune(qc.vote_info.parent_id)
            self.getMaxRound(qc, self.high_commit_qc, True)

        self.getMaxRound(qc, self.high_qc, False)

    def execute_and_insert(self, b):

        if b.qc is None:
            self.validator_info["Ledger"].speculate(-1, b.id, b.payload)
        else:
            self.validator_info["Ledger"].speculate(b.qc.vote_info.id, b.id, b.payload)

        self.pending_block_tree[b.id] = b

    def process_vote(self, v):

        if self.process_qc(v.high_commit_qc) == False:
            return None

        vote_idx = self.hash(v.ledger_commit_info.commit_state_id, v.ledger_commit_info.vote_info_hash)

        if vote_idx in self.pending_votes:
            self.pending_votes[vote_idx].append(v.signature)
        else:
            self.pending_votes[vote_idx] = [v.signature]

        if len(self.pending_votes[vote_idx]) >= (
                2 * self.faulty_validators) + 1:  # 3 (2*f)+1: # need to set f from workload_configuration.json

            signatures_list = list(self.pending_votes[vote_idx])
            author_sign = self.validator_info["Main"]["signature_dict"]["private_key"].sign(
                self.generateSignRecur(signatures_list).encode('utf-8'))
            new_qc = QC(v.vote_info, v.ledger_commit_info, signatures_list, self.validator_info["Main"]["u"],
                        author_sign)  # str(self.validator_info["Main"]["u"] )=> author will sign list of signature

            self.logToFile(str("Validator: " + self.validator_info["Main"]["u"] + " created QC message"),
                           LoggingLevel.INFO)
            return new_qc
        return None

    def generateSignRecur(self, signatures_list):
        hash_of_all_sign = ''
        for i in range(0, len(signatures_list)):
            hash_of_all_sign = str(hash(str(hash(signatures_list[i])) + hash_of_all_sign))

        return hash_of_all_sign

    def generate_block(self, transactions, current_round):

        author = self.validator_info["Main"]["u"]
        curr_round = current_round

        payload = transactions
        qc = self.high_qc

        if qc is not None:
            vote_info_id = qc.vote_info.id
            qc_signatures = qc.signatures
        else:
            vote_info_id = -1
            qc_signatures = []

        hash_id = self.hash(author, curr_round, payload, vote_info_id, qc_signatures)  # Crypto
        block = Block(author, curr_round, payload, qc, hash_id)

        return block

    def hash(self, a="", b="", c="", d="", e=""):
        return hash(str(a) + str(e) + str(b) + str(c) + str(d))

    def prune(self, parent_block_id):

        if parent_block_id not in self.validator_info["Ledger"].blockid_ledger_map:
            return

        parent_ledger_state_id = self.validator_info["Ledger"].blockid_ledger_map[parent_block_id]
        list_of_ledger_ids = []

        for key, val in self.validator_info["Ledger"].blockid_ledger_map.items():

            if val == parent_ledger_state_id:
                break
            list_of_ledger_ids.append(val)

        for ledger_id in list_of_ledger_ids:
            if ledger_id in self.validator_info["Ledger"].pending_ledger_states:
                del self.validator_info["Ledger"].pending_ledger_states[ledger_id]

    def verifySignature(self, sender, signed_msg, generated_hexcode_signed_msg, client=False):
        if client == False:
            verify_key = VerifyKey(self.validator_info["Main"]["signature_dict"]["validators_public_key"][sender])
        else:
            verify_key = VerifyKey(self.validator_info["Main"]["signature_dict"]["clients_public_key"][sender])

        try:
            verify_key.verify(signed_msg)
        except:
            print("Signature was forged or corrupt in vote msg sent by", sender)
            return False

        if signed_msg.message != generated_hexcode_signed_msg:
            print("Packet  content was forged or corrupt sent by", sender)
            return False

        return True

    def logToFile(self, msg, level):
        f = open(self.validator_info["Main"]["logger_file"], "a")
        msg = "[" + level.name + "]: " + strftime("%Y-%m-%d %H:%M:%S ", gmtime()) + "  \t\t " + "[ " + msg + " ]\n"
        f.write(msg)
        f.close()
