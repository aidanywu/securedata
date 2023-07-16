from web3 import Web3
from web3.auto import w3
import os
import json
from solcx import compile_standard, install_solc, compile_source
import solcx
from geth import LoggingMixin, DevGethProcess
from geth.accounts import ensure_account_exists
from geth.wrapper import construct_test_chain_kwargs
from geth.chain import get_chain_data_dir
from pathlib import Path
import time
import shutil
import _thread

class Geth(LoggingMixin, DevGethProcess):
    pass


def initChain():
    print("-------------------------initing chain---------------")
    base_dir = Path(__file__).parent.parent.absolute() / 'chainData'
    if os.path.exists(base_dir):
        print("-----------deleting base dir------------------------")
        shutil.rmtree(base_dir)
        time.sleep(1)
    log_dir = Path(__file__).parent.parent.absolute() / 'logs'
    if os.path.exists(log_dir):
        print("-----------deleting log dir------------------------")
        shutil.rmtree(log_dir)
        time.sleep(1)
    chain_name = "data"
    password_file = str(Path(__file__).parent.parent.absolute() / 'password') # can be stored anywhere
    overrides = {
        'network_id': "7653",
        'port': "30303",
        'unlock':  None,
        'password': password_file,
        #'password': None,
        'mine': False, 
        'no_discover': False,
        'max_peers': None,
        'verbosity': None,
        'allow_insecure_unlock': True,
        ## RPC
        'rpc_enabled': True,
        'rpc_addr': "0.0.0.0",
        # 'rpc_api': "db,net,eth,web3,personal", # default is all APIs
        'rpc_port': "8545",
        'rpc_cors_domain': '*',
        ## WS
        'ws_enabled': False,
        'ws_addr': None,
        'ws_api': None,
        'ws_port': None,
        'ipc_disable': True,
        'ipc_path': None,
    }
    datadir = get_chain_data_dir(base_dir, chain_name)
    # weird way to create an account first but necessary to initialize with ether
    coinbase = ensure_account_exists(**construct_test_chain_kwargs(data_dir=datadir, **overrides)).decode()
    genesis_data = {
        "config": {
            "chainId": 7653,
            "homesteadBlock": 0,
            "eip150Block": 0,
            "eip155Block": 0,
            "eip158Block": 0,
            "byzantiumBlock": 0,
            "constantinopleBlock": 0,
            "petersburgBlock": 0,
            "istanbulBlock": 0,
            "berlinBlock": 0,
            "londonBlock": 0,
            "daoForkBlock": 0,
            "daoForSupport": True,
        },
        "coinbase": coinbase,
        "difficulty": "0x200",
        "extraData": "",
        "gasLimit": "0x2fefd8",
        "nonce": "0x0000000000000087",
        "mixhash": "0x0000000000000000000000000000000000000000000000000000000000000000",
        "parentHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
        "timestamp": "0x00",
        "alloc": {
            coinbase: {"balance": "100000000000000000000"},
        },
    }
    geth = Geth(chain_name, base_dir, overrides, genesis_data)
    accs = geth.accounts
    print("accounts:", accs)
    print("coinbase:", coinbase)
    geth.start()
    key_path = datadir + "/keystore/"
    with open(key_path + os.listdir(key_path)[0]) as keyfile:
        encrypted = keyfile.read()
        password = open(password_file).read()
        print("password:", password)
        private_key = w3.eth.account.decrypt(encrypted,password).hex()
        print("private_key:", private_key)
    return coinbase, private_key

def compile_contracts(file_path, contract_name, libraries_address=""):
    with open(file_path, "r") as file:
        source_code = file.read()
        compiled_sol = compile_source(
            source = source_code, 
            base_path = "./contracts",
            output_values=["abi", "bin"],
            solc_version = "0.8.17"
        )
        abi = compiled_sol["<stdin>:{}".format(contract_name)]['abi']
        bytecode = compiled_sol["<stdin>:{}".format(contract_name)]['bin']
        
        print("Contracts {} compiled".format(contract_name))
        return bytecode, abi

def mine(web3, miner_account, length):
    if web3.eth.mining:
        web3.geth.miner.stop()
    web3.geth.miner.set_gas_price('0x19999999')
    web3.geth.miner.set_etherbase(miner_account['address'])
    web3.geth.miner.start(4)
    time.sleep(length)
    web3.geth.miner.stop()

def __init():
    coinbase, private_key = initChain()
    time.sleep(2)

    global web3
    web3 = Web3(Web3.HTTPProvider(r'http://127.0.0.1:8545'))
    print("HTTP Provider Created!")

    global account_from
    account_from = {
        'private_key': private_key,
        'address': Web3.to_checksum_address(coinbase),
    }
    print(account_from)
    print("balance of coinbase:", web3.eth.get_balance(account_from["address"]))

    _thread.start_new_thread(mine, (web3, account_from, 600))
    
    global chainID
    chainID = 7653

    solcx.install_solc("0.8.17")

    # deploy DateTime
    
    bytecode_DT, abi_DT = compile_contracts(r'./contracts/DateTime.sol', "DateTime")
    contract_DT = web3.eth.contract(abi=abi_DT, bytecode=bytecode_DT)
    nonce = web3.eth.get_transaction_count(account_from['address'])
    try:
        transaction = contract_DT.constructor().build_transaction(
            {
                "chainId": chainID,
                "gasPrice": web3.eth.gas_price,
                "gas": 200000,
                "from": account_from['address'],
                "nonce": nonce,
            }
        )
    except Exception as e:
        print(e)
    else:
        print('11111111111111111111111111111')
    try:
        signed_txn = web3.eth.account.sign_transaction(transaction, private_key=account_from['private_key'])
    except Exception as e:
        print(e)
    else:
        print('22222222222222222222222222222')
    try:
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    except Exception as e:
        print(e)
    else:
        print('33333333333333333333333333333')
    try:
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    except Exception as e:
        print(e)
    else:
        print('44444444444444444444444444444')
    DT_contract_address = tx_receipt.contractAddress

    # compile contracts
    try:
        bytecode_PV, abi_PV = compile_contracts(r'./contracts/PermissionValidator.sol', "PermissionValidator", DT_contract_address)
        bytecode_AC, abi_AC = compile_contracts(r'./contracts/AccessControl.sol', "AccessControl", DT_contract_address)
        bytecode_AR, abi_AR = compile_contracts(r'./contracts/AccessRecord.sol', "AccessRecord", DT_contract_address)
    except Exception as e:
        print(e)
    try:
        print("PV functions:")
        for func in abi_PV:
            if func['type'] == 'function':
                print(func['name'])
        print("\nAC functions:")
        for func in abi_AC:
            if func['type'] == 'function':
                print(func['name'])
        print("\nAR functions:")
        for func in abi_AR:
            if func['type'] == 'function':
                print(func['name'])
    except Exception as e:
        print(e)

    # deploy PV
    contract_PV = web3.eth.contract(abi=abi_PV, bytecode=bytecode_PV)
    nonce = web3.eth.get_transaction_count(account_from['address'])
    transaction = contract_PV.constructor().build_transaction(
        {
            "chainId": chainID,
            "gasPrice": web3.eth.gas_price,
            "from": account_from['address'],
            "nonce": nonce,
        }
    )
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=account_from['private_key'])
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    PV_contract_address = tx_receipt.contractAddress
    print("contract PV deployed")


    # deploy AC
    contract_AC = web3.eth.contract(abi=abi_AC, bytecode=bytecode_AC)
    nonce = web3.eth.get_transaction_count(account_from['address'])
    transaction = contract_AC.constructor(PV_contract_address).build_transaction(
        {
            "chainId": chainID,
            "gasPrice": web3.eth.gas_price,
            "from": account_from['address'],
            "nonce": nonce,
        }
    )
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=account_from['private_key'])
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    AC_contract_address = tx_receipt.contractAddress
    print("contract AC deployed")


    # deploy AR
    contract_AR = web3.eth.contract(abi=abi_AR, bytecode=bytecode_AR)
    nonce = web3.eth.get_transaction_count(account_from['address'])
    transaction = contract_AR.constructor(PV_contract_address).build_transaction(
        {
            "chainId": chainID,
            "gasPrice": web3.eth.gas_price,
            "from": account_from['address'],
            "nonce": nonce,
        }
    )
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=account_from['private_key'])
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    AR_contract_address = tx_receipt.contractAddress
    print("contract AR deployed")

    global AC, AR, PV
    PV = web3.eth.contract(abi = abi_PV, address=PV_contract_address)
    AC = web3.eth.contract(abi = abi_AC, address=AC_contract_address)
    AR = web3.eth.contract(abi = abi_AR, address=AR_contract_address)

    print("final amount in coinbase:", web3.eth.get_balance(account_from["address"]))


def getInstance():
    global AC, AR, PV, web3, account_from, chainId
    # time.sleep(10)
    # _thread.start_new_thread(mine, (web3, account_from, 10))
    return AC, AR, PV, web3, account_from, chainID