
class TrafficGate:
    def __init__(self, max_valid_per_window=10):
        self.max_valid_per_window = max_valid_per_window

    def filter_window(self, packets, flooding=False):
        accepted = []
        rejected = []

        for packet in packets:
            reason = None

            if packet.get("bad_sig", 1) != 0:
                reason = "BAD_SIGNATURE"

            elif packet.get("ip_mismatch", 1) != 0:
                reason = "IP_MISMATCH"

            elif flooding and len(accepted) >= self.max_valid_per_window:
                reason = "RATE_LIMIT"

            if reason:
                rejected.append((packet, reason))
            else:
                accepted.append(packet)

        return accepted, rejected
