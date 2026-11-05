
from pathlib import Path
import shutil

# M6 performance instrumentation
target = Path("m4_enforcement.py")
backup = Path("m4_enforcement_before_timing.py")

original = target.read_text()

if "M6_TIMING_INSTRUMENTED" in original:
    raise SystemExit("Timing code already installed.")

changes = [
    (
        "        result = subprocess.run(\n",
        "        firewall_started = time.perf_counter()\n"
        "        result = subprocess.run(\n"
    ),
    (
        "        _last_block = time.monotonic()\n",
        "        firewall_ms = (\n"
        "            time.perf_counter() - firewall_started\n"
        "        ) * 1000\n"
        "        _last_block = time.monotonic()\n"
    ),
    (
        "        # Record confirmed firewall enforcement on blockchain\n"
        "        try:\n",
        "        # Record confirmed firewall enforcement on blockchain\n"
        "        chain_started = time.perf_counter()\n"
        '        chain_status = "FAILED"\n'
        "        try:\n"
    ),
    (
        '            print("ENFORCED BLOCKCHAIN TX:", tx_hash)\n',
        '            chain_status = "CONFIRMED"\n'
        '            print("ENFORCED BLOCKCHAIN TX:", tx_hash)\n'
    ),
    (
        '        print(\n            "M4 ENFORCED:",',
        '''        chain_ms = (
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
            "M4 ENFORCED:",'''
    )
]

updated = original

for old, new in changes:
    if updated.count(old) != 1:
        raise SystemExit(
            "Expected code section not found. "
            "Original file was not changed."
        )
    updated = updated.replace(old, new, 1)

updated = "# M6_TIMING_INSTRUMENTED\n" + updated

# Check syntax before changing the working file.
compile(updated, str(target), "exec")

# Preserve existing work.
if not backup.exists():
    shutil.copy2(target, backup)

target.write_text(updated)

print("M6 timing instrumentation installed.")
print("Backup:", backup)
print("Updated:", target)
print("Next: run Python syntax verification.")
