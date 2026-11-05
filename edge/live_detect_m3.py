
import csv
import os
from datetime import datetime

import joblib
import core
import config
import mitigation

# Load the trained AI model
bundle = joblib.load("models/isolation_forest_m3.joblib")
model = bundle["model"]
feature_names = bundle["features"]

indices = [
    core.FEATURES.index(name)
    for name in feature_names
]

# Security alert logging
logfile = "live_alerts.csv"
new_file = not os.path.exists(logfile) or os.path.getsize(logfile) == 0

with open(logfile, "a", newline="") as f:
    writer = csv.writer(f)

    if new_file:
        writer.writerow([
            "timestamp", "ip", "count",
            "bad_sig_frac", "ip_mismatch_frac", "reasons"
        ])

    print("Live IoT security detection started.")
    print("AI model loaded successfully.")
    print("Mitigation mode: DRY_RUN")
    print("Press Ctrl+C to stop.")

    try:
        for batch in core.windows():
            for ip, (features, packets) in batch.items():

                if features[0] == 0:
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

                if reasons:
                    print("ALERT:", ip, reasons)

                    # Record dry-run mitigation decision
                    mitigation.record(ip, reasons)

                    # Save security alert
                    writer.writerow([
                        datetime.now().isoformat(),
                        ip,
                        features[0],
                        features[6],
                        features[7],
                        "|".join(reasons)
                    ])
                    f.flush()
                else:
                    print("NORMAL:", ip, "count:", features[0])

    except KeyboardInterrupt:
        print("\nLive detector stopped.")

