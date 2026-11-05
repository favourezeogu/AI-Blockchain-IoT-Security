
import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

import joblib
import core
import config
import mitigation
import registry_client
import m4_enforcement

from traffic_gate import TrafficGate

# ============================================
# ADVANCED BROADBAND COMMUNICATIONS PROJECT
# AI + BLOCKCHAIN + IoT SECURITY
# AUTOMATIC MITIGATION SYSTEM
# ============================================

BASE = Path(__file__).resolve().parent

# ============================================
# 1. LOAD TRAINED ISOLATION FOREST MODEL
# ============================================

bundle = joblib.load(
    BASE / "models/isolation_forest_m3.joblib"
)

model = bundle["model"]

indices = [
    core.FEATURES.index(name)
    for name in bundle["features"]
]

# ============================================
# 2. INITIALIZE APPLICATION TRAFFIC GATE
# ============================================

gate = TrafficGate(
    max_valid_per_window=10
)

# ============================================
# 3. CSV FILE WRITER
# ============================================

def make_writer(file, header):

    writer = csv.writer(file)

    if file.tell() == 0:
        writer.writerow(header)

    return writer

# ============================================
# 4. OPEN SECURITY AND TRAFFIC LOG FILES
# ============================================

with (
    open(BASE / "live_alerts.csv", "a", newline="") as alert_file,
    open(BASE / "traffic_gate_windows.csv", "a", newline="") as gate_file,
    open(BASE / "trusted_sensor_data.csv", "a", newline="") as trusted_file,
    open(BASE / "registry_rejections.csv", "a", newline="") as registry_file
):

    alert_writer = make_writer(
        alert_file,
        [
            "timestamp",
            "ip",
            "count",
            "bad_sig_frac",
            "ip_mismatch_frac",
            "reasons"
        ]
    )

    gate_writer = make_writer(
        gate_file,
        [
            "timestamp",
            "ip",
            "received",
            "accepted",
            "rejected",
            "flooding"
        ]
    )

    trusted_writer = make_writer(
        trusted_file,
        [
            "timestamp",
            "ip",
            "device_id",
            "value",
            "size",
            "packet_timestamp"
        ]
    )

    registry_writer = make_writer(
        registry_file,
        [
            "timestamp",
            "ip",
            "device_id",
            "reason",
            "rejected_packets"
        ]
    )

    # ========================================
    # 5. DISPLAY SYSTEM STARTUP INFORMATION
    # ========================================

    print("=======================================")
    print("ADVANCED BROADBAND IoT SECURITY SYSTEM")
    print("=======================================")

    print("Isolation Forest AI: ENABLED")
    print("HMAC Validation: ENABLED")
    print("Identity Spoofing Detection: ENABLED")
    print("Flooding Detection: ENABLED")
    print("Application Traffic Gate: ENABLED")
    print("Blockchain Authorization: ENABLED")
    print("M4 Firewall Enforcement: ENABLED")
    print("Mitigation Decision Logging: DRY_RUN")

    print("=======================================")
    print("Press Ctrl+C to stop.")
    print("=======================================")

    # ========================================
    # 6. START LIVE IOT TRAFFIC PROCESSING
    # ========================================

    try:

        for batch in core.windows():

            for ip, (features, packets) in batch.items():

                if not packets:
                    continue

                timestamp = datetime.now().isoformat()

                reasons = []

                # =================================
                # 7. AI ANOMALY DETECTION
                # =================================

                x = [
                    [float(features[i]) for i in indices]
                ]

                prediction = model.predict(x)[0]

                if prediction == -1:
                    reasons.append("AI_ANOMALY")

                # =================================
                # 8. SECURITY RULE DETECTION
                # =================================

                # Invalid HMAC indicates tampering
                if features[6] > 0:
                    reasons.append("BAD_SIGNATURE")

                # Unexpected device/source IP
                if features[7] > 0:
                    reasons.append("IP_MISMATCH")

                # High packet count indicates flooding
                if features[0] >= config.FLOOD_COUNT:
                    reasons.append("FLOODING")

                # =================================
                # 9. APPLICATION TRAFFIC GATE
                # =================================

                flooding = "FLOODING" in reasons

                accepted, rejected = gate.filter_window(
                    packets,
                    flooding=flooding
                )

                # =================================
                # 10. BLOCKCHAIN DEVICE AUTHORIZATION
                # =================================

                authorization_cache = {}

                approved = []
                registry_rejected = []

                for packet in accepted:

                    device_id = packet.get("id")

                    if (
                        not isinstance(device_id, str)
                        or not device_id
                    ):

                        denial = "MISSING_DEVICE_ID"

                    else:

                        if device_id not in authorization_cache:

                            try:

                                authorization_cache[device_id] = (
                                    registry_client.is_authorized(
                                        device_id
                                    )
                                )

                            except Exception as error:

                                print(
                                    "Blockchain authorization error:",
                                    error
                                )

                                authorization_cache[device_id] = None

                        status = authorization_cache[device_id]

                        if status is True:

                            denial = None

                        elif status is False:

                            denial = "UNAUTHORIZED_DEVICE"

                        else:

                            denial = "BLOCKCHAIN_UNAVAILABLE"

                    if denial is None:

                        approved.append(packet)

                    else:

                        rejected.append(
                            (packet, denial)
                        )

                        registry_rejected.append(
                            (packet, denial)
                        )

                accepted = approved

                # =================================
                # 11. SAVE AUTHORIZED SENSOR DATA
                # =================================

                for packet in accepted:

                    trusted_writer.writerow([
                        timestamp,
                        ip,
                        packet.get("id"),
                        packet.get("val"),
                        packet.get("size"),
                        packet.get("ts")
                    ])

                # =================================
                # 12. SAVE TRAFFIC GATE STATISTICS
                # =================================

                gate_writer.writerow([
                    timestamp,
                    ip,
                    len(packets),
                    len(accepted),
                    len(rejected),
                    int(flooding)
                ])

                # =================================
                # 13. RECORD REGISTRY REJECTIONS
                # =================================

                denied_counts = Counter(
                    (
                        str(packet.get("id")),
                        reason
                    )
                    for packet, reason in registry_rejected
                )

                for (device_id, reason), count in denied_counts.items():

                    registry_writer.writerow([
                        timestamp,
                        ip,
                        device_id,
                        reason,
                        count
                    ])

                    print(
                        "REGISTRY REJECT:",
                        device_id,
                        reason,
                        count
                    )

                # =================================
                # 14. COMBINE SECURITY REASONS
                # =================================

                all_reasons = list(
                    dict.fromkeys(
                        reasons + [
                            reason
                            for _, reason in registry_rejected
                        ]
                    )
                )

                # =================================
                # 15. SAVE SECURITY ALERTS
                # =================================

                if all_reasons:

                    print(
                        "ALERT:",
                        ip,
                        all_reasons
                    )

                    alert_writer.writerow([
                        timestamp,
                        ip,
                        features[0],
                        features[6],
                        features[7],
                        "|".join(all_reasons)
                    ])

                # =================================
                # 16. AUTOMATIC FIREWALL MITIGATION
                # =================================

                if reasons:

                    try:

                        enforcement_status = (
                            m4_enforcement.enforce(
                                ip,
                                reasons
                            )
                        )

                    except Exception as error:

                        enforcement_status = "BLOCK_FAILED"

                        print(
                            "M4 Enforcement Error:",
                            error
                        )

                    print(
                        "M4 ENFORCEMENT STATUS:",
                        enforcement_status
                    )

                    # Existing mitigation decision logger
                    # records DRY_RUN security decisions

                    try:

                        mitigation.record(
                            ip,
                            reasons
                        )

                    except Exception as error:

                        print(
                            "Mitigation logging error:",
                            error
                        )

                # =================================
                # 17. DISPLAY TRAFFIC STATISTICS
                # =================================

                print(
                    "TRAFFIC:",
                    ip,
                    "received:", len(packets),
                    "accepted:", len(accepted),
                    "rejected:", len(rejected)
                )

                # =================================
                # 18. SAVE DATA TO DISK
                # =================================

                alert_file.flush()
                gate_file.flush()
                trusted_file.flush()
                registry_file.flush()

    except KeyboardInterrupt:

        print(
            "\nAI + Blockchain detector stopped."
        )
