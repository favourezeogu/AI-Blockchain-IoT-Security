
import csv
import joblib
import config

bundle = joblib.load("models/isolation_forest_m3.joblib")
model = bundle["model"]
names = bundle["features"]

files = [
    "data_normal_session2.csv",
    "data_tamper.csv",
    "data_spoof_retry2.csv",
    "data_flood_test.csv"
]

for filename in files:
    with open(filename) as f:
        rows = list(csv.DictReader(f))

    X = [
        [float(row[name]) for name in names]
        for row in rows
    ]

    predictions = model.predict(X)

    ai_flags = [p == -1 for p in predictions]

    rule_flags = [
        float(r["bad_sig_frac"]) > 0
        or float(r["ip_mismatch_frac"]) > 0
        or float(r["count"]) >= config.FLOOD_COUNT
        for r in rows
    ]

    hybrid_flags = [
        ai or rule
        for ai, rule in zip(ai_flags, rule_flags)
    ]

    print("\nDataset:", filename)
    print("Total windows:", len(rows))
    print("AI-only flags:", sum(ai_flags))
    print("Rules-only flags:", sum(rule_flags))
    print("Hybrid flags:", sum(hybrid_flags))
