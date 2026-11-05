
import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

if not w3.is_connected():
    raise SystemExit("Ganache is not connected")

with open("../build/contracts/SecurityEventLog.json") as f:
    artifact = json.load(f)

chain_id = str(w3.eth.chain_id)
address = artifact["networks"][chain_id]["address"]

contract = w3.eth.contract(
    address=Web3.to_checksum_address(address),
    abi=artifact["abi"]
)

admin = contract.functions.admin().call()

tx_hash = contract.functions.logSecurityEvent(
    "lab-test-dev1",
    "REJECT_INVALID_PACKET",
    "TEST_ONLY_BAD_SIGNATURE",
    0,
    True
).transact({"from": admin})

receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

events = contract.events.SecurityEventLogged().process_receipt(receipt)

print("Transaction status:", receipt.status)
print("Transaction hash:", tx_hash.hex())
print("Block number:", receipt.blockNumber)
print("Recorded event count:", contract.functions.eventCount().call())
print("Event emitted:", len(events) == 1)
