
import csv
from datetime import datetime

import joblib
import core
import config
import mitigation
from traffic_gate import TrafficGate

# Load existing trained AI model
bundle = joblib.load("models/isolation_forest_m3.joblib")
model = bundle["model"]

indices = [
    core.FEATURES.index(name)
    for name in bundle["features"]
]

# Application-level traffic gate
gate = TrafficGate(max_valid_per_window=10)

def make_writer(file, header):
    writer = csv.writer(file)

    if file.tell() == 0:
        writer.writerow(header)

    return writer

with (
    open("live_alerts.csv", "a", newline="") as alert_file,
    open("traffic_gate_windows.csv", "a", newline="") as gate_file,
    open("trusted_sensor_data.csv", "a", newline="") as trusted_file
):
    alert_writer = make_writer(
        alert_file,
        [
            "timestamp", "ip", "count",
            "bad_sig_frac", "ip_mismatch_frac",
            "reasons"
        ]
    )

    gate_writer = make_writer(
        gate_file,
        [
            "timestamp", "ip", "received",
            "accepted", "rejected", "flooding"
        ]
    )

    trusted_writer = make_writer(
        trusted_file,
        [
            "timestamp", "ip", "device_id",
            "value", "size", "packet_timestamp"
        ]
    )

    print("LIVE IoT DETECTION AND TRAFFIC GATE STARTED")
    print("Mode: APPLICATION-LEVEL ENFORCEMENT")
    print("Press Ctrl+C to stop.")

    try:
        for batch in core.windows():
            for ip, (features, packets) in batch.items():
                if not packets:
                    continue

                x = [[float(features[i]) for i in indices]]
                reasons = []

                if model.predict(x)[0] == -1:
                    reasons.append("AI_ANOMALY")

                if features[6] > 0:
                    reasons.append("BAD_SIGNATURE")

                if features[7] > 0:
                    reasons.append("IP_MISMATCH")

                if features[0] >= config.FLOOD_COUNT:
                    reasons.append("FLOODING")

                flooding = "FLOODING" in reasons

                accepted, rejected = gate.filter_window(
                    packets,
                    flooding=flooding
                )

                timestamp = datetime.now().isoformat()

                # Trusted output contains accepted packets only
                for packet in accepted:
                    trusted_writer.writerow([
                        timestamp,
                        ip,
                        packet.get("id"),
                        packet.get("val"),
                        packet.get("size"),
                        packet.get("ts")
                    ])

                # Save traffic admission statistics
                gate_writer.writerow([
                    timestamp,
                    ip,
                    len(packets),
                    len(accepted),
                    len(rejected),
                    int(flooding)
                ])

                print(
                    "TRAFFIC:", ip,
                    "received:", len(packets),
                    "accepted:", len(accepted),
                    "rejected:", len(rejected)
                )

                if reasons:
                    print("ALERT:", ip, reasons)

                    mitigation.record(ip, reasons)

                    alert_writer.writerow([
                        timestamp,
                        ip,
                        features[0],
                        features[6],
                        features[7],
                        "|".join(reasons)
                    ])

                alert_file.flush()
                gate_file.flush()
                trusted_file.flush()

    except KeyboardInterrupt:
        print("\nLive traffic gate stopped.")
