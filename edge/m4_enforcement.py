# M6_TIMING_INSTRUMENTED

import csv
import subprocess
import time
from datetime import datetime
from pathlib import Path

import config
import blockchain_logger

HELPER = "/usr/local/sbin/m4-block-iot"
LOG = Path(__file__).resolve().parent / "m4_enforcement.csv"

BLOCK_SECONDS = 30
COOLDOWN_SECONDS = 35

_last_block = 0.0

TRIGGERS = {
    "BAD_SIGNATURE",
    "IP_MISMATCH",
    "FLOODING"
}

def record_event(ip, action, reasons, detail):
    new_file = not LOG.exists() or LOG.stat().st_size == 0

    with LOG.open("a", newline="") as f:
        writer = csv.writer(f)

        if new_file:
            writer.writerow([
                "timestamp", "ip", "action",
                "reasons", "detail"
            ])

        writer.writerow([
            datetime.now().isoformat(),
            ip,
            action,
            "|".join(reasons),
            detail
        ])

def enforce(ip, reasons):
    global _last_block

    # Never block based only on an AI anomaly.
    if not TRIGGERS.intersection(reasons):
        return "REVIEW_ONLY"

    # This helper is restricted to the lab Raspberry Pi.
    if ip != "192.168.1.179":
        return "SOURCE_NOT_ALLOWED"

    # Refuse to run if project configuration has changed.
    if config.DEVICE_IPS.get("dev1") != ip:
        return "CONFIG_IP_MISMATCH"

    now = time.monotonic()

    if now - _last_block < COOLDOWN_SECONDS:
        return "COOLDOWN"

    try:
        firewall_started = time.perf_counter()
        result = subprocess.run(
            ["sudo", "-n", HELPER],
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )

        if result.returncode != 0:
            detail = result.stderr.strip() or "Helper failed"

            record_event(
                ip, "BLOCK_FAILED", reasons, detail
            )

            print("M4 ENFORCEMENT ERROR:", detail)

            return "BLOCK_FAILED"

        firewall_ms = (
            time.perf_counter() - firewall_started
        ) * 1000
        _last_block = time.monotonic()

        record_event(
            ip,
            "UDP_BLOCK_ENFORCED",
            reasons,
            "UDP port 5005; timeout 30 seconds"
        )
           
        # Record confirmed firewall enforcement on blockchain
        chain_started = time.perf_counter()
        chain_status = "FAILED"
        try:
            tx_hash = blockchain_logger.log_security_event(
                ip,
                "UDP_BLOCK_ENFORCED",
                reasons,
                dry_run=False
            )

            chain_status = "CONFIRMED"
            print("ENFORCED BLOCKCHAIN TX:", tx_hash)

        except Exception as error:
            print(
                "Firewall block applied, but blockchain logging failed:",
                error
            )


        chain_ms = (
            time.perf_counter() - chain_started
        ) * 1000

        performance_file = (
            Path(__file__).resolve().parent
            / "m6_performance.csv"
        )

        try:
            with performance_file.open(
                "a", newline=""
            ) as f:
                writer = csv.writer(f)

                if f.tell() == 0:
                    writer.writerow([
                        "timestamp",
                        "ip",
                        "reasons",
                        "firewall_ms",
                        "blockchain_ms",
                        "blockchain_status"
                    ])

                writer.writerow([
                    datetime.now().isoformat(),
                    ip,
                    "|".join(reasons),
                    round(firewall_ms, 3),
                    round(chain_ms, 3),
                    chain_status
                ])

        except OSError as error:
            print("M6 timing save error:", error)

        print(
            "M6 TIMING:",
            "Firewall:", round(firewall_ms, 3), "ms",
            "Blockchain:", round(chain_ms, 3), "ms",
            "Status:", chain_status
        )

        print(
            "M4 ENFORCED:",
            ip,
            "UDP port 5005 blocked for 30 seconds"
        )


        return "UDP_BLOCK_ENFORCED"

    except Exception as error:
        record_event(
            ip, "BLOCK_FAILED", reasons, str(error)
        )

        print("M4 ENFORCEMENT ERROR:", error)

        return "BLOCK_FAILED"
