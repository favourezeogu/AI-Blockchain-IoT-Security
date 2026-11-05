import socket, json, time, hmac, hashlib
from collections import defaultdict
import numpy as np
import config

FEATURES = ["count", "mean_size", "mean_iat", "std_iat",
            "val_mean", "val_std", "bad_sig_frac", "ip_mismatch_frac"]

def verify(msg, key):
    body = f'{msg["id"]}|{msg["seq"]}|{float(msg["val"]):.2f}|{msg["ts"]}'
    exp = hmac.new(key.encode(), body.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(exp, str(msg.get("sig", "")))

def packet_stream():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 4 * 1024 * 1024)
    sock.bind(("0.0.0.0", config.UDP_PORT))
    sock.settimeout(0.5)
    while True:
        try:
            data, (ip, _) = sock.recvfrom(4096)
        except socket.timeout:
            yield None
            continue
        yield time.time(), ip, data

def parse(ts, ip, data):
    p = dict(ts=ts, ip=ip, size=len(data), val=0.0, bad_sig=1, ip_mismatch=1, id=None)
    try:
        msg = json.loads(data)
        dev = msg.get("id")
        p["id"] = dev
        p["val"] = float(msg.get("val", 0))
        key = config.KEYS.get(dev)
        p["bad_sig"] = 0 if (key and verify(msg, key)) else 1
        p["ip_mismatch"] = 0 if config.DEVICE_IPS.get(dev) == ip else 1
    except Exception:
        pass
    return p

def features(pk):
    n = len(pk)
    t = np.sort([p["ts"] for p in pk])
    iat = np.diff(t) if n > 1 else np.array([float(config.WINDOW_SEC)])
    v = np.array([p["val"] for p in pk])
    return [n,
            float(np.mean([p["size"] for p in pk])),
            float(iat.mean()), float(iat.std()),
            float(v.mean()), float(v.std()),
            float(np.mean([p["bad_sig"] for p in pk])),
            float(np.mean([p["ip_mismatch"] for p in pk]))]

def windows():
    buf, start = defaultdict(list), time.time()
    for item in packet_stream():
        if item:
            buf[item[1]].append(parse(*item))
        if time.time() - start >= config.WINDOW_SEC:
            out = {ip: (features(p), p) for ip, p in buf.items()}
            buf.clear()
            start = time.time()
            yield out
