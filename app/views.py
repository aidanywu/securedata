from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse, JsonResponse
from django.template import Context, loader
from ethdata.settings import *
from web3 import Web3
import json

from app import contracts_op as conOp

conOp.__init()

def index(request):
    return render(request, "test.html")


def addUserEntry(request):
    # NOTICE: when it is a write function, we need build a transaction and sign it

    userID = request.GET.get('userid') 
    entryID = request.GET.get('entryid')

    AC, AR, PV, web3, account_from, chainID = conOp.getInstance()

    # 3. Call addUserEntry and Build tx 

    tx = AC.functions.addUserEntry(userID, entryID).build_transaction(
        {
            # "gas": 200000,
            'gasPrice': web3.eth.gas_price,
            'chainId': chainID,
            'from': account_from['address'],
            'nonce': web3.eth.get_transaction_count(account_from['address']),
        }
    )

    # 4. Sign tx with PK
    tx_create = web3.eth.account.sign_transaction(tx, account_from['private_key'])

    # 5. Send tx and wait for receipt
    tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return JsonResponse({'message':'OK'})
    

def getUserEntry(request):
    AC, AR, PV, web3, account_from, chainID = conOp.getInstance()
    userID = request.GET.get('userid')

    # NOTICE: when it is a read function, we can just call it
    result = AC.functions.getUserEntry(userID).call()
    return JsonResponse({'message':'OK', 'result':result})


def removeUserEntry(request):
    AC, AR, PV, web3, account_from, chainID = conOp.getInstance()
    userID = request.GET.get('userid')
    entryID = request.GET.get('entryid')
    tx = AC.functions.removeUserEntry(userID, entryID).build_transaction(
        {
            # "gas": 200000,
            'gasPrice': web3.eth.gas_price,
            'chainId': chainID,
            'from': account_from['address'],
            'nonce': web3.eth.get_transaction_count(account_from['address']),
        }
    )
    tx_create = web3.eth.account.sign_transaction(tx, account_from['private_key'])
    tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return JsonResponse({'message':'OK', 'transactionHash': tx_hash.hex()})

def removeAllEntry(request):
    AC, AR, PV, web3, account_from, chainID = conOp.getInstance()
    userID = request.GET.get('userid')
    tx = AC.functions.removeAllEntry(userID).build_transaction(
        {
            # "gas": 200000,
            'gasPrice': web3.eth.gas_price,
            'chainId': chainID,
            'from': account_from['address'],
            'nonce': web3.eth.get_transaction_count(account_from['address']),
        }
    )
    tx_create = web3.eth.account.sign_transaction(tx, account_from['private_key'])
    tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return JsonResponse({'message':'OK', 'transactionHash': tx_hash.hex()})

def validateUserEntry(request):
    AC, AR, PV, web3, account_from, chainID = conOp.getInstance()
    userID = request.GET.get('userid')
    entryID = request.GET.get('entryid')
    result = AC.functions.validateUserEntry(userID, entryID).call()
    return JsonResponse({'message':'OK', 'result':result})



def addRecord(request):
    AC, AR, PV, web3, account_from, chainID = conOp.getInstance()
    userID = request.GET.get('userid')
    entryID = request.GET.get('entryid')
    tx = AR.functions.addRecord(userID, entryID).build_transaction(
        {
            # "gas": 200000,
            'gasPrice': web3.eth.gas_price,
            'chainId': chainID,
            'from': account_from['address'],
            'nonce': web3.eth.get_transaction_count(account_from['address']),
        }
    )
    tx_create = web3.eth.account.sign_transaction(tx, account_from['private_key'])
    tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return JsonResponse({'message':'OK', 'transactionHash': tx_hash.hex()})

def removeOutDateRecord(request):
    AC, AR, PV, web3, account_from, chainID = conOp.getInstance()
    tx = AR.functions.removeOutDateRecord().build_transaction(
        {
            # "gas": 200000,
            'gasPrice': web3.eth.gas_price,
            'chainId': chainID,
            'from': account_from['address'],
            'nonce': web3.eth.get_transaction_count(account_from['address']),
        }
    )
    tx_create = web3.eth.account.sign_transaction(tx, account_from['private_key'])
    tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return JsonResponse({'message':'OK', 'transactionHash': tx_hash.hex()})

def showAll(request):
    AC, AR, PV, web3, account_from, chainID = conOp.getInstance()
    result = AR.functions.showAll().call()
    return JsonResponse({'message':'OK', 'result':result})

def addAdmin(request):
    AC, AR, PV, web3, account_from, chainID = conOp.getInstance()
    newAdmin = request.GET.get('newAdmin')
    tx = PV.functions.addAdmin(newAdmin).build_transaction(
        {
            # "gas": 200000,
            'gasPrice': web3.eth.gas_price,
            'chainId': chainID,
            'from': account_from['address'],
            'nonce': web3.eth.get_transaction_count(account_from['address']),
        }
    )
    tx_create = web3.eth.account.sign_transaction(tx, account_from['private_key'])
    tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return JsonResponse({'message':'OK', 'transactionHash': tx_hash.hex()})

def removeAdmin(request):
    AC, AR, PV, web3, account_from, chainID = conOp.getInstance()
    admin = request.GET.get('admin')
    tx = PV.functions.removeAdmin(admin).build_transaction(
        {
            # "gas": 200000,
            'gasPrice': web3.eth.gas_price,
            'chainId': chainID,
            'from': account_from['address'],
            'nonce': web3.eth.get_transaction_count(account_from['address']),
        }
    )
    tx_create = web3.eth.account.sign_transaction(tx, account_from['private_key'])
    tx_hash = web3.eth.send_raw_transaction(tx_create.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    return JsonResponse({'message':'OK', 'transactionHash': tx_hash.hex()})

def isReady(request):
    AC, AR, PV, web3, account_from, chainID = conOp.getInstance()
    result = PV.functions.isReady().call()
    print(result, type(result))
    return JsonResponse({'message':'OK', 'result':result})