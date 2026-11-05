
import json
from pathlib import Path
from web3 import Web3

URL = "http://127.0.0.1:8545"

def is_authorized(device_id):
    w3 = Web3(Web3.HTTPProvider(
        URL,
        request_kwargs={"timeout": 3}
    ))

    if not w3.is_connected():
        raise ConnectionError("Ganache disconnected")

    path = (
        Path(__file__).resolve().parent.parent
        / "build/contracts/DeviceRegistry.json"
    )

    with path.open() as f:
        artifact = json.load(f)

    deployment = artifact["networks"].get(
        str(w3.eth.chain_id)
    )

    if not deployment:
        raise RuntimeError("Registry not deployed")

    address = Web3.to_checksum_address(
        deployment["address"]
    )

    if not w3.eth.get_code(address):
        raise RuntimeError("Registry contract missing")

    contract = w3.eth.contract(
        address=address,
        abi=artifact["abi"]
    )

    return contract.functions.isAuthorized(
        device_id
    ).call()

if __name__ == "__main__":
    print("dev1 authorized:", is_authorized("dev1"))
    print("unknown authorized:", is_authorized("unknown"))
