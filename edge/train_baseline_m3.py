import csv
import joblib
from sklearn.ensemble import IsolationForest

FEATURES = [
    "count", "mean_size", "mean_iat",
    "std_iat", "val_mean", "val_std"
]

def load_data(filename):
    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        return [
            [float(row[name]) for name in FEATURES]
            for row in reader
        ]

train = load_data("data_normal.csv")
test = load_data("data_normal_session2.csv")

model = IsolationForest(
    n_estimators=200,
    contamination=0.03,
    random_state=42
)
model.fit(train)

predictions = model.predict(test)
alerts = sum(p == -1 for p in predictions)
rate = 100 * alerts / len(test)

print("Training records:", len(train))
print("Normal test records:", len(test))
print("Normal records flagged as anomalies:", alerts)
print(f"Normal-data false alert rate: {rate:.2f}%")

joblib.dump(
    {"model": model, "features": FEATURES},
    "models/isolation_forest_m3.joblib"
)
print("Model saved successfully.")
