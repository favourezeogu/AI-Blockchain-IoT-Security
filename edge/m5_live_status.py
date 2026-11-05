
import csv
import json
import subprocess
from pathlib import Path

import streamlit as st
import config
import registry_client

BASE = Path(__file__).resolve().parent

STATUS_HELPER = "/usr/local/sbin/m5-iot-status"

def contains_ip(value, ip):
    if isinstance(value, dict):
        return any(
            contains_ip(item, ip)
            for item in value.values()
        )

    if isinstance(value, list):
        return any(
            contains_ip(item, ip)
            for item in value
        )

    return value == ip

def is_firewall_blocked(ip):
    result = subprocess.run(
        ["sudo", "-n", STATUS_HELPER],
        capture_output=True,
        text=True,
        timeout=6
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stderr.strip() or
            "Firewall status unavailable"
        )

    data = json.loads(result.stdout)

    for entry in data.get("nftables", []):
        firewall_set = entry.get("set", {})

        if firewall_set.get("name") == "blocked_ipv4":
            return contains_ip(
                firewall_set.get("elem", []),
                ip
            )

    raise RuntimeError("IoT firewall set not found")

@st.fragment(run_every="5s")
def render():

    st.divider()
    st.header("8. Live IoT Device Security Status")

    device_id = "dev1"
    device_ip = config.DEVICE_IPS.get(
        device_id, "Unknown"
    )

    st.write("Device:", device_id)
    st.write("Configured IP:", device_ip)

    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Blockchain Authorization")

        try:
            authorized = registry_client.is_authorized(
                device_id
            )

            if authorized:
                st.success("AUTHORIZED")
            else:
                st.error("UNAUTHORIZED")

        except Exception as error:
            st.warning("Blockchain status unavailable")
            st.caption(str(error))

    with c2:
        st.subheader("Current Firewall Status")

        try:
            blocked = is_firewall_blocked(device_ip)

            if blocked:
                st.error("BLOCKED - UDP PORT 5005")
            else:
                st.success("NOT CURRENTLY BLOCKED")

        except Exception as error:
            st.warning("Firewall status unavailable")
            st.caption(str(error))

    st.subheader("Last Enforced Mitigation")

    path = BASE / "m4_enforcement.csv"

    if path.exists():

        with path.open(newline="") as file:
            records = list(csv.DictReader(file))

        enforced = [
            row for row in records
            if row.get("action") == "UDP_BLOCK_ENFORCED"
        ]

        if enforced:
            latest = enforced[-1]

            st.write("Timestamp:", latest["timestamp"])
            st.write("Source IP:", latest["ip"])
            st.write("Action:", latest["action"])
            st.write("Reason:", latest["reasons"])

        else:
            st.info("No enforced mitigation recorded.")

    else:
        st.info("No enforcement history found.")

    st.caption(
        "Current status refreshes every 5 seconds. "
        "The last enforcement record is historical "
        "and does not mean the device remains blocked."
    )
