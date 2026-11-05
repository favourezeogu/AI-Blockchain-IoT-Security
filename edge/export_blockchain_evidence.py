
import json
from pathlib import Path
from web3 import Web3

base = Path(__file__).resolve().parent
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

if not w3.is_connected():
    raise SystemExit("Ganache is not connected")

artifact_path = base.parent / "build/contracts/SecurityEventLog.json"

with open(artifact_path) as f:
    artifact = json.load(f)

address = artifact["networks"][str(w3.eth.chain_id)]["address"]

contract = w3.eth.contract(
    address=Web3.to_checksum_address(address),
    abi=artifact["abi"]
)

events = contract.events.SecurityEventLogged().get_logs(
    from_block=0,
    to_block="latest"
)

records = []

for event in events:
    args = event["args"]
    records.append({
        "device": args["deviceId"],
        "action": args["action"],
        "reason": args["reason"],
        "dry_run": args["dryRun"],
        "transaction_hash": event["transactionHash"].hex(),
        "block_number": event["blockNumber"]
    })

output = base.parent / "evidence/blockchain_events.json"

with open(output, "w") as f:
    json.dump(records, f, indent=2)

print("Blockchain events exported:", len(records))
print("Saved to:", output)
