from django.test import TestCase, Client
from django.urls import reverse
import sys
import time
from app import contracts_op as conOp
import web3 as w3
from web3.exceptions import ContractLogicError
# from web3.utils import randomHex

# Create your tests here.

print('i am here')

"""
    Run using: python manage.py test app.tests.TestAPIs.runTest
"""
class TestAPIs(TestCase):
    def setUp(self):
        sys.stderr.write("SetUp--------------------"+'\n')
        self.AC, self.AR, self.PV, self.web3, _, self.chainID = conOp.getInstance()
        acc = self.web3.eth.account.create()
        self.admin = {
            "name": "admin",
            "address": w3.Web3.to_checksum_address(acc.address),
            "private_key": acc.key.hex()
        }
        sys.stderr.write(repr(self.admin)+'\n')
        acc = self.web3.eth.account.create()
        self.nonadmin = {
            "name": "nonadmin",
            "address": w3.Web3.to_checksum_address(acc.address),
            "private_key": acc.key.hex()
        }
        sys.stderr.write(repr(self.nonadmin)+'\n')
        self.accs = [self.admin, self.nonadmin]
        self.users = ['person1', 'person2']
        self.client = Client()
        """
            Run this function only
        """
    def runTest(self):
        sys.stderr.write("isReady------------------"+'\n')
        self.isReady()
        sys.stderr.write("addUserEntryAndGet-------"+'\n')
        self.addUserEntryAndGet()
        sys.stderr.write("removeUserEntryAndGet----"+'\n')
        self.removeUserEntryAndGet()
        sys.stderr.write("validateUserEntry--------"+'\n')
        self.validateUserEntry()
        sys.stderr.write("removeAllEntry-----------"+'\n')
        self.removeAllEntry()
        sys.stderr.write("addRecordAndShowAll------"+'\n')
        self.addRecordAndShowAll()
        sys.stderr.write("addAdminAndremoveAdmin---"+'\n')
        self.addAdminAndremoveAdmin()
        sys.stderr.write("startMining--------------"+'\n')
        self.startMining()
        sys.stderr.write("addVid-------------------"+'\n')
        self.addVid()
        sys.stderr.write("removeVid----------------"+'\n')
        self.removeVid()
        sys.stderr.write("removeAllVid-------------"+'\n')
        self.removeAllVid()
        sys.stderr.write("addRec-------------------"+'\n')
        self.addRec()
        sys.stderr.write("addAdmin-----------------"+'\n')
        self.addAdmin()
        sys.stderr.write("removeAdmin--------------"+'\n')
        self.removeAdmin()
        sys.stderr.write("stopMining---------------"+'\n')
        self.stopMining()
    # confirm that the contracts are deployed and ready
    def isReady(self):
        response = self.client.get("/app/isReady")
        sys.stderr.write(repr(response.content)+'\n')
        self.assertEqual(response.status_code, 200)
    """
        Testing AccessControl
    """
    def addUserEntryAndGet(self):
        for userid in self.users:
            for i in range(7):
                response = self.client.get("/app/addUserEntry", {'userid':userid,"entryid":"entry{}".format(i)})
                sys.stderr.write(repr(response.content)+'\n')
                self.assertEqual(response.status_code, 200)
                response = self.client.get("/app/getUserEntry", {'userid':userid})
                sys.stderr.write(repr(response.content)+'\n')
                self.assertEqual(response.status_code, 200)
                # time.sleep(30)
    def removeUserEntryAndGet(self):
        for userid in self.users:
            for i in range(3):
                response = self.client.get("/app/removeUserEntry", {'userid':userid,"entryid":"entry{}".format(i)})
                sys.stderr.write(repr(response.content)+'\n')
                self.assertEqual(response.status_code, 200)
                response = self.client.get("/app/getUserEntry", {'userid':userid})
                sys.stderr.write(repr(response.content)+'\n')
                self.assertEqual(response.status_code, 200)
    def validateUserEntry(self):
        for userid in self.users:
            for i in range(2,4):
                response = self.client.get("/app/validateUserEntry", {'userid':userid,"entryid":"entry{}".format(i)})
                sys.stderr.write(repr(response.content)+'\n')
                self.assertEqual(response.status_code, 200)
    def removeAllEntry(self):
        response = self.client.get("/app/removeAllEntry", {'userid':self.users[0]})
        sys.stderr.write(repr(response.content)+'\n')
        self.assertEqual(response.status_code, 200)
        for userid in self.users:
            response = self.client.get("/app/getUserEntry", {'userid':userid})
            sys.stderr.write(repr(response.content)+'\n')
            self.assertEqual(response.status_code, 200)
    """
        Testing AccessRecord
    """
    def addRecordAndShowAll(self):
        for userid in self.users:
            for i in range(3):
                response = self.client.get("/app/addRecord", {'userid':userid,"entryid":"entry{}".format(i)})
                sys.stderr.write(repr(response.content)+'\n')
                self.assertEqual(response.status_code, 200)
                response = self.client.get("/app/showAll")
                sys.stderr.write(repr(response.content)+'\n')
                self.assertEqual(response.status_code, 200)
                # time.sleep(30)
    # not sure how to test removeOutDateRecord
    """
        Testing Permission Validator
    """
    def addAdminAndremoveAdmin(self):
        response = self.client.get("/app/addAdmin", {'newAdmin':self.admin['address']})
        sys.stderr.write(repr(response.content)+'\n')
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/app/addAdmin", {'newAdmin':self.nonadmin['address']})
        sys.stderr.write(repr(response.content)+'\n')
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/app/removeAdmin", {'admin':self.nonadmin['address']})
        sys.stderr.write(repr(response.content)+'\n')
        self.assertEqual(response.status_code, 200)
    """
        Testing Permissions
    """
    def startMining(self): # make sure contracts are mined
        n = 15
        for acc in self.accs: # so each acc has enough ether to send contracts
            sys.stderr.write("Mining %d sec for %s"%(n,acc['name']) + '\n')
            self.web3.geth.miner.set_etherbase(acc['address'])
            self.web3.geth.miner.start(4)
            time.sleep(n)
            self.web3.geth.miner.stop()
        if self.web3.eth.mining:
            self.web3.geth.miner.stop()
        self.web3.geth.miner.set_etherbase(self.admin['address'])
        self.web3.geth.miner.start(4)
    # AC
    def addVid(self):
        for acc in self.accs:
            for i in range(3):
                try:
                    tx = self.AC.functions.addUserEntry(acc["name"], 'entry{}'.format(i)).build_transaction(
                        {
                            'gasPrice': self.web3.eth.gas_price,
                            'chainId': self.chainID,
                            'from': acc['address'],
                            'nonce': self.web3.eth.get_transaction_count(acc['address']),
                        }
                    )
                    tx_create = self.web3.eth.account.sign_transaction(tx, acc['private_key'])
                    tx_hash = self.web3.eth.send_raw_transaction(tx_create.rawTransaction)
                    tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
                except ContractLogicError as e:
                    sys.stderr.write(acc["name"] + " cannot addUserEntry: " + repr(e) +'\n')
                    # break
                else:
                    sys.stderr.write(acc["name"] + " can addUserEntry: " + tx_hash.hex() +'\n')
    def removeVid(self):
        for acc in self.accs:
            for i in range(1):
                try:
                    tx = self.AC.functions.removeUserEntry(acc["name"], 'entry{}'.format(i)).build_transaction(
                        {
                            'gasPrice': self.web3.eth.gas_price,
                            'chainId': self.chainID,
                            'from': acc['address'],
                            'nonce': self.web3.eth.get_transaction_count(acc['address']),
                        }
                    )
                    tx_create = self.web3.eth.account.sign_transaction(tx, acc['private_key'])
                    tx_hash = self.web3.eth.send_raw_transaction(tx_create.rawTransaction)
                    tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
                except ContractLogicError as e:
                    sys.stderr.write(acc["name"] + " cannot removeUserEntry: " + repr(e) +'\n')
                    # break
                else:
                    sys.stderr.write(acc["name"] + " can removeUserEntry:" + tx_hash.hex() +'\n')
    def removeAllVid(self):
        for acc in self.accs:
            try:
                tx = self.AC.functions.removeAllEntry(acc["name"]).build_transaction(
                    {
                        'gasPrice': self.web3.eth.gas_price,
                        'chainId': self.chainID,
                        'from': acc['address'],
                        'nonce': self.web3.eth.get_transaction_count(acc['address']),
                    }
                )
                tx_create = self.web3.eth.account.sign_transaction(tx, acc['private_key'])
                tx_hash = self.web3.eth.send_raw_transaction(tx_create.rawTransaction)
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            except ContractLogicError as e:
                sys.stderr.write(acc["name"] + " cannot removeAllEntry: " + repr(e) +'\n')
            else:
                sys.stderr.write(acc["name"] + " can removeAllEntry: " + tx_hash.hex() +'\n')
    # AR
    def addRec(self):
        for acc in self.accs:
            for i in range(3):
                try:
                    tx = self.AR.functions.addRecord(acc["name"], 'entry{}'.format(i)).build_transaction(
                        {
                            'gasPrice': self.web3.eth.gas_price,
                            'chainId': self.chainID,
                            'from': acc['address'],
                            'nonce': self.web3.eth.get_transaction_count(acc['address']),
                        }
                    )
                    tx_create = self.web3.eth.account.sign_transaction(tx, acc['private_key'])
                    tx_hash = self.web3.eth.send_raw_transaction(tx_create.rawTransaction)
                    tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
                except ContractLogicError as e:
                    sys.stderr.write(acc["name"] + " cannot addRecord: " + repr(e) +'\n')
                else:
                    sys.stderr.write(acc["name"] + " can addRecord: " + tx_hash.hex() +'\n')
    # PV
    def addAdmin(self):
        for acc in self.accs:
            try:
                tx = self.PV.functions.addAdmin(self.nonadmin["address"]).build_transaction(
                    {
                        'gasPrice': self.web3.eth.gas_price,
                        'chainId': self.chainID,
                        'from': acc['address'],
                        'nonce': self.web3.eth.get_transaction_count(acc['address']),
                    }
                )
                tx_create = self.web3.eth.account.sign_transaction(tx, acc['private_key'])
                tx_hash = self.web3.eth.send_raw_transaction(tx_create.rawTransaction)
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            except ContractLogicError as e:
                sys.stderr.write(acc["name"] + " cannot addAdmin: " + repr(e) +'\n')
            else:
                sys.stderr.write(acc["name"] + " can addAdmin: " + tx_hash.hex() +'\n')
    def removeAdmin(self):
        for acc in self.accs:
            try:
                tx = self.PV.functions.removeAdmin(self.admin["address"]).build_transaction(
                    {
                        'gasPrice': self.web3.eth.gas_price,
                        'chainId': self.chainID,
                        'from': acc['address'],
                        'nonce': self.web3.eth.get_transaction_count(acc['address']),
                    }
                )
                tx_create = self.web3.eth.account.sign_transaction(tx, acc['private_key'])
                tx_hash = self.web3.eth.send_raw_transaction(tx_create.rawTransaction)
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            except ContractLogicError as e:
                sys.stderr.write(acc["name"] + " cannot removeAdmin: " + repr(e) +'\n')
            else:
                sys.stderr.write(acc["name"] + " can removeAdmin: " + tx_hash.hex() +'\n')
    def stopMining(self): # tests done so stop mining
       self.web3.geth.miner.stop()