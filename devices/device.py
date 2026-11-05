import socket, json, time, hmac, hashlib, random, sys

def sign(dev, key, seq, val, ts):
    body = f"{dev}|{seq}|{val:.2f}|{ts}"
    return hmac.new(key.encode(), body.encode(), hashlib.sha256).hexdigest()

def packet(dev, key, seq, val):
    ts = int(time.time() * 1000)
    msg = {"id": dev, "seq": seq, "val": val, "ts": ts,
           "sig": sign(dev, key, seq, val, ts)}
    return json.dumps(msg).encode()

if __name__ == "__main__":
    # usage: python device.py dev1 key1-secret 192.168.1.121
    dev, key, host = sys.argv[1:4]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seq = 0
    while True:
        seq += 1
        val = round(random.gauss(25, 1.5), 2)
        s.sendto(packet(dev, key, seq, val), (host, 5005))
        time.sleep(random.uniform(0.4, 0.6))
