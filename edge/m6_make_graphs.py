
import csv
import shutil
import statistics
from pathlib import Path

import matplotlib.pyplot as plt

BASE = Path(__file__).resolve().parent
SOURCE = BASE / "m6_performance.csv"
OUTPUT = BASE.parent / "evidence" / "milestone6"

OUTPUT.mkdir(parents=True, exist_ok=True)

with SOURCE.open(newline="") as file:
    rows = list(csv.DictReader(file))

rows = [
    r for r in rows
    if r["blockchain_status"] == "CONFIRMED"
]

if not rows:
    raise SystemExit("No confirmed results found")

trials = list(range(1, len(rows) + 1))

firewall = [
    float(r["firewall_ms"]) for r in rows
]

blockchain = [
    float(r["blockchain_ms"]) for r in rows
]

def save_bar_chart(values, title, filename):
    plt.figure(figsize=(9, 5))
    plt.bar(
        [f"Test {i}" for i in trials],
        values
    )
    plt.ylabel("Latency (milliseconds)")
    plt.title(title)
    plt.ylim(bottom=0)
    plt.tight_layout()
    plt.savefig(OUTPUT / filename, dpi=200)
    plt.close()

# Graph 1: Firewall latency
save_bar_chart(
    firewall,
    "IoT Firewall Activation Latency",
    "m6_firewall_latency.png"
)

# Graph 2: Blockchain latency
save_bar_chart(
    blockchain,
    "Blockchain Transaction Confirmation Latency",
    "m6_blockchain_latency.png"
)

# Graph 3: Side-by-side comparison
width = 0.35

plt.figure(figsize=(9, 5))

plt.bar(
    [x - width / 2 for x in trials],
    firewall,
    width,
    label="Firewall"
)

plt.bar(
    [x + width / 2 for x in trials],
    blockchain,
    width,
    label="Blockchain"
)

plt.xticks(
    trials,
    [f"Test {i}" for i in trials]
)

plt.ylabel("Latency (milliseconds)")
plt.title("Firewall vs Blockchain Processing Time")
plt.legend()
plt.tight_layout()

plt.savefig(
    OUTPUT / "m6_latency_comparison.png",
    dpi=200
)
plt.close()

# Generate numerical summary
summary = []

for name, values in [
    ("Firewall", firewall),
    ("Blockchain", blockchain)
]:
    summary.extend([
        name,
        f"Trials: {len(values)}",
        f"Mean: {statistics.mean(values):.3f} ms",
        f"Minimum: {min(values):.3f} ms",
        f"Maximum: {max(values):.3f} ms",
        f"Sample SD: {statistics.stdev(values):.3f} ms"
        if len(values) > 1 else "Sample SD: N/A",
        ""
    ])

(OUTPUT / "m6_performance_summary.txt").write_text(
    "\n".join(summary)
)

shutil.copy2(
    SOURCE,
    OUTPUT / "m6_performance.csv"
)

print("M6 GRAPHS CREATED SUCCESSFULLY")
print("Saved in:", OUTPUT)

for name in [
    "m6_firewall_latency.png",
    "m6_blockchain_latency.png",
    "m6_latency_comparison.png",
    "m6_performance_summary.txt"
]:
    print(name)
