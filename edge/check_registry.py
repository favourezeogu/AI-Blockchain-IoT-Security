
import json
from web3 import Web3

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

if not w3.is_connected():
    raise SystemExit("Ganache is not connected")

with open("../build/contracts/DeviceRegistry.json") as f:
    artifact = json.load(f)

network = artifact["networks"].get(str(w3.eth.chain_id))

if not network:
    raise SystemExit("DeviceRegistry deployment not found")

address = Web3.to_checksum_address(network["address"])

if not w3.eth.get_code(address):
    raise SystemExit("No contract found at this address")

registry = w3.eth.contract(
    address=address,
    abi=artifact["abi"]
)

device = registry.functions.devices("dev1").call()

print("Blockchain connected")
print("Chain ID:", w3.eth.chain_id)
print("Device: dev1")
print("Registered:", device[0])
print("Authorized:", device[1])
print("Credit:", device[2])
print("Mitigation actions:",
      registry.functions.actionCount().call())
