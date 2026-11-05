
import csv
import json
import statistics
import subprocess
from datetime import datetime
from pathlib import Path

from web3 import Web3
import config
import registry_client

# ==========================================
# ADVANCED BROADBAND COMMUNICATIONS
# FINAL PROJECT SYSTEM VERIFICATION
# ==========================================

BASE = Path(__file__).resolve().parent
EVIDENCE = BASE.parent / "evidence"
OUTPUT = EVIDENCE / "milestone6"

OUTPUT.mkdir(parents=True, exist_ok=True)

results = []

def report(message):
    print(message)
    results.append(message)

report("ADVANCED BROADBAND PROJECT")
report("FINAL SYSTEM VERIFICATION")
report("Date: " + datetime.now().isoformat())
report("=" * 45)

# ==========================================
# 1. CHECK AI MODEL
# ==========================================

model_path = (
    BASE / "models/isolation_forest_m3.joblib"
)

report("\n1. AI INTRUSION DETECTION")

if model_path.exists():
    report("AI Model: FOUND")
else:
    report("AI Model: MISSING")

# ==========================================
# 2. CHECK BLOCKCHAIN
# ==========================================

report("\n2. BLOCKCHAIN CONNECTION")

try:
    w3 = Web3(
        Web3.HTTPProvider(
            "http://127.0.0.1:8545",
            request_kwargs={"timeout": 5}
        )
    )

    if w3.is_connected():
        report("Ganache: CONNECTED")
        report("Chain ID: " + str(w3.eth.chain_id))
    else:
        report("Ganache: DISCONNECTED")

except Exception as error:
    report("Blockchain error: " + str(error))

# ==========================================
# 3. DEVICE AUTHORIZATION
# ==========================================

report("\n3. IOT DEVICE AUTHORIZATION")

device_id = "dev1"
device_ip = config.DEVICE_IPS.get(device_id)

report("Device: " + device_id)
report("Configured IP: " + str(device_ip))

try:
    authorized = registry_client.is_authorized(
        device_id
    )

    report("Authorized: " + str(authorized))

except Exception as error:
    report("Authorization error: " + str(error))

# ==========================================
# 4. CURRENT FIREWALL STATUS
# ==========================================

report("\n4. FIREWALL STATUS")

try:
    result = subprocess.run(
        [
            "sudo",
            "-n",
            "/usr/local/sbin/m5-iot-status"
        ],
        capture_output=True,
        text=True,
        timeout=6
    )

    if result.returncode == 0:

        data = json.loads(result.stdout)

        firewall_sets = [
            item["set"]
            for item in data.get("nftables", [])
            if "set" in item
            and item["set"].get("name") == "blocked_ipv4"
        ]

        if firewall_sets:
            report("IoT Firewall: AVAILABLE")
            report(
                "Active blocked entries: "
                + str(len(firewall_sets[0].get("elem", [])))
            )
        else:
            report("IoT Firewall: SET NOT FOUND")

    else:
        report(
            "Firewall status error: "
            + result.stderr.strip()
        )

except Exception as error:
    report("Firewall check error: " + str(error))

# ==========================================
# 5. PERFORMANCE MEASUREMENTS
# ==========================================

report("\n5. M6 PERFORMANCE RESULTS")

performance_path = BASE / "m6_performance.csv"

if performance_path.exists():

    with performance_path.open(newline="") as f:
        rows = list(csv.DictReader(f))

    confirmed = [
        row for row in rows
        if row["blockchain_status"] == "CONFIRMED"
    ]

    report(
        "Confirmed experiments: "
        + str(len(confirmed))
    )

    if confirmed:

        firewall = [
            float(row["firewall_ms"])
            for row in confirmed
        ]

        blockchain = [
            float(row["blockchain_ms"])
            for row in confirmed
        ]

        report(
            "Average firewall activation: "
            + f"{statistics.mean(firewall):.3f} ms"
        )

        report(
            "Average blockchain confirmation: "
            + f"{statistics.mean(blockchain):.3f} ms"
        )

else:
    report("Performance dataset: MISSING")

# ==========================================
# 6. CHECK GRAPHICAL RESULTS
# ==========================================

report("\n6. GRAPHICAL EVIDENCE")

graph_files = [
    "m6_firewall_latency.png",
    "m6_blockchain_latency.png",
    "m6_latency_comparison.png"
]

for filename in graph_files:

    path = OUTPUT / filename

    status = "SAVED" if path.exists() else "MISSING"

    report(filename + ": " + status)

# ==========================================
# 7. CHECK DASHBOARD
# ==========================================

report("\n7. STREAMLIT DASHBOARD FILES")

for filename in [
    "dashboard.py",
    "m5_live_status.py",
    "m4_enforcement.csv"
]:

    status = (
        "FOUND"
        if (BASE / filename).exists()
        else "MISSING"
    )

    report(filename + ": " + status)

# ==========================================
# 8. SAVE VERIFICATION REPORT
# ==========================================

output_file = OUTPUT / "final_verification.txt"

output_file.write_text(
    "\n".join(results) + "\n"
)

print("\nFINAL VERIFICATION COMPLETED")
print("Saved to:", output_file)
