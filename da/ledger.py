from collections import defaultdict
from collections import OrderedDict
from time import gmtime, strftime

import enum
class LoggingLevel(enum.Enum):
    NOTSET=0
    DEBUG=1
    INFO=2
    WARNING=3
    ERROR=4
    CRITICAL=5

# validator_info  : consists of all the items which we  were accessing via Main.initializer
# validator_info {
#   Main
# }

class Ledger:
    def __init__(self, pending_ledger_states, persistent_ledger_states, blockid_ledger_map, persistent_ledger_file,
                 persistent_ledger_tracker, validator_info=None):
        self.validator_info = validator_info
        self.pending_ledger_states = pending_ledger_states#defaultdict()  # key: ledger_state_id, value:[block_id, txns] #need to verify if block id has to be added
        self.persistent_ledger_states = persistent_ledger_states# defaultdict()
        # key is block_id and value is corresponding ledger_state_id.
        self.blockid_ledger_map = blockid_ledger_map#OrderedDict()
        self.persistent_ledger_file=persistent_ledger_file

        self.persistent_ledger_tracker = persistent_ledger_tracker

    def setValidator_info(self,validator_info):
        self.validator_info = validator_info
        self.clear_file()

    def speculate(self, prev_block_id, block_id, txns):
        # hashing to create the ledger state id.
        if prev_block_id not in self.blockid_ledger_map:
            ledger_state_id = str(-1) + str(txns)  ## need to verify
        else:
            ledger_state_id = str(self.blockid_ledger_map[prev_block_id]) + str(txns)

        ledger_state_id=hash(ledger_state_id)
        self.blockid_ledger_map[block_id] = ledger_state_id
        self.pending_ledger_states[ledger_state_id] = [block_id, txns]

    def pending_state(self, block_id):
        if block_id in self.blockid_ledger_map:
            return self.blockid_ledger_map[block_id]  # need to verify

    def commit(self, block_id):
        if block_id in self.blockid_ledger_map and self.blockid_ledger_map[block_id] in  self.pending_ledger_states:

            self.persistent_ledger_states[self.blockid_ledger_map[block_id]] = self.pending_ledger_states[self.blockid_ledger_map[block_id]]
            self.writeToFile(self.blockid_ledger_map[block_id],self.pending_ledger_states[self.blockid_ledger_map[block_id]])
            self.validator_info["Mempool"].update_transaction(str(self.pending_ledger_states[self.blockid_ledger_map[block_id]][1][0]), 'COMPLETE')
            # print("Writing to file")
            print(self.validator_info["Main"]["u"], " commiting transaction : ", self.pending_ledger_states[self.blockid_ledger_map[block_id]][1])
            for trans in self.pending_ledger_states[self.blockid_ledger_map[block_id]][1]:
                self.validator_info["Main"]["results"][str(trans)] = "COMPLETED"
                self.validator_info["Main"]["client_results"][str(trans)] = "COMPLETED"
            if self.blockid_ledger_map[block_id] in self.pending_ledger_states:
                del self.pending_ledger_states[self.blockid_ledger_map[block_id]]
        else:
            pass

    def committed_block(self, block_id):

        if block_id in self.validator_info["BlockTree"].pending_block_tree:
            return self.validator_info["BlockTree"].pending_block_tree[block_id]

    def clear_file(self):
        f = open(self.persistent_ledger_file,"a")
        msg = "\n \n " + self.validator_info["Main"]["comment_for_test_case"] + " \n \n"
        f.write(msg)
        f.close()

    def writeToFile(self,key,value):

        transaction = []
        for t in value[1]:
            if t not in self.persistent_ledger_tracker:
                transaction.append(t)
                self.persistent_ledger_tracker.add(t)

        f = open(self.persistent_ledger_file, "a")
        msg = "\nNew Commit: " + self.validator_info["Main"]["u"] + " ledger_state_id: " + str(
            key) + " block_id: " + str(value[0]) + " Transaction: " + str(transaction)
        self.logToFile(str("Validator: " + self.validator_info["Main"]["u"] + " adding commit for transaction: "+str(transaction)), LoggingLevel.INFO)

        f.write(msg)
        f.close()

    def logToFile(self,msg, level):
        f = open(self.validator_info["Main"]["logger_file"], "a")
        msg = "[" + level.name + "]: " + strftime("%Y-%m-%d %H:%M:%S ", gmtime()) + "  \t\t " + "[ " + msg + " ]\n"
        f.write(msg)
        f.close()