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
#Not needed here
#validator_info  : consists of all the items which we  were accessing via Main.initializer
# validator_info {
#   "Main" : {}
# }

class Mempool:
    def __init__(self,validator_info=None):
        self.validator_info=validator_info
        self.transactions = defaultdict() # this will be filled when a validator is initialized via runner

    def setValidator_info(self,validator_info):
        self.validator_info = validator_info

    def get_transactions(self,):
        list_of_pending_transactions=[]
        for k, v in self.transactions.items():
            if v == "PENDING":
                list_of_pending_transactions.append(k)

        return list_of_pending_transactions

    def add_transaction(self,M,state):
        if M is None:
            return
        self.logToFile(str("Validator: " + self.validator_info["Main"]["u"] + " adding transaction: " + M),LoggingLevel.INFO)

        self.transactions[M]=state

    def update_transaction(self, M, state):
        if M in self.transactions:
            self.transactions[M] = state


    def logToFile(self,msg, level):
        f = open(self.validator_info["Main"]["logger_file"], "a")
        msg = "[" + level.name + "]: " + strftime("%Y-%m-%d %H:%M:%S ", gmtime()) + "  \t\t " + "[ " + msg + " ]\n"
        f.write(msg)
        f.close()