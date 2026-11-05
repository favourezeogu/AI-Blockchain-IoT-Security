
import json
from pathlib import Path
from web3 import Web3

ARTIFACT = (
    Path(__file__).resolve().parent.parent
    / "build/contracts/SecurityEventLog.json"
)

def log_security_event(ip, action, reasons, dry_run=True):
    w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

    if not w3.is_connected():
        raise ConnectionError("Ganache is not connected")

    with open(ARTIFACT) as f:
        artifact = json.load(f)

    address = artifact["networks"][str(w3.eth.chain_id)]["address"]

    contract = w3.eth.contract(
        address=Web3.to_checksum_address(address),
        abi=artifact["abi"]
    )

    if len(w3.eth.get_code(contract.address)) == 0:
        raise RuntimeError("Contract is not deployed")

    admin = contract.functions.admin().call()

    tx_hash = contract.functions.logSecurityEvent(
        "source-ip:" + ip,
        action,
        "|".join(reasons),
        0,
        dry_run
    ).transact({"from": admin})

    receipt = w3.eth.wait_for_transaction_receipt(
        tx_hash, timeout=30
    )

    if receipt.status != 1:
        raise RuntimeError("Blockchain transaction failed")

    return tx_hash.hex()
