import csv, sys
import core, config

label = sys.argv[1] if len(sys.argv) > 1 else "normal"
only_ip = sys.argv[2] if len(sys.argv) > 2 else None

with open(f"data_{label}.csv", "a", newline="") as f:
    w = csv.writer(f)
    if f.tell() == 0:
        w.writerow(core.FEATURES + ["ip", "label"])
    print(f"Collecting '{label}' windows... Ctrl+C to stop")
    for out in core.windows():
        for ip, (feat, _) in out.items():
            if only_ip and ip != only_ip:
                continue
            w.writerow(feat + [ip, label])
            f.flush()
            print(ip, [round(x, 2) for x in feat])
