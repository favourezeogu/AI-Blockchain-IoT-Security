import time
import blockchain_logger

_last_chain_log = {}
import csv
from datetime import datetime
from pathlib import Path

LOG = Path("mitigation_actions.csv")

def record(ip, reasons):
    if "BAD_SIGNATURE" in reasons:
        action = "REJECT_INVALID_PACKET"
    elif "IP_MISMATCH" in reasons:
        action = "QUARANTINE_IDENTITY"
    elif "FLOODING" in reasons:
        action = "RATE_LIMIT"
    else:
        action = "REVIEW_AI_ANOMALY"

    new_file = not LOG.exists() or LOG.stat().st_size == 0

    with LOG.open("a", newline="") as f:
        writer = csv.writer(f)

        if new_file:
            writer.writerow([
                "timestamp", "ip", "mode",
                "action", "reasons"
            ])

        writer.writerow([
            datetime.now().isoformat(),
            ip, "DRY_RUN", action,
            "|".join(reasons)
        ])

    print("MITIGATION (DRY_RUN):", ip, action)
    key = (ip, action)
    now = time.monotonic()

    if now - _last_chain_log.get(key, -1e9) >= 30:
        _last_chain_log[key] = now

        try:
            tx_hash = blockchain_logger.log_security_event(
                ip, action, reasons
            )
            print("BLOCKCHAIN TX:", tx_hash)
        except Exception as error:
            print("Blockchain logging error:", error)
