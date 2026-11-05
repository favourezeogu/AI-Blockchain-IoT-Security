
import csv
import json
from pathlib import Path

import streamlit as st
from web3 import Web3

BASE = Path(__file__).resolve().parent

st.set_page_config(
    page_title="IoT Security Dashboard",
    page_icon="🛡️",
    layout="wide"
)

st.title("IoT AI and Blockchain Security Dashboard")
st.caption("Raspberry Pi 5 | Ubuntu | Isolation Forest | Ganache")

def read_csv(filename):
    path = BASE / filename
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))

def read_blockchain():
    try:
        w3 = Web3(Web3.HTTPProvider(
            "http://127.0.0.1:8545",
            request_kwargs={"timeout": 3}
        ))

        if not w3.is_connected():
            return [], "Ganache disconnected"

        path = BASE.parent / "build/contracts/SecurityEventLog.json"

        with path.open() as f:
            artifact = json.load(f)

        address = artifact["networks"][str(w3.eth.chain_id)]["address"]

        contract = w3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=artifact["abi"]
        )

        if not w3.eth.get_code(contract.address):
            return [], "Contract not deployed on current chain"

        events = contract.events.SecurityEventLogged().get_logs(
            from_block=0,
            to_block="latest"
        )

        records = []
        for event in events:
            args = event["args"]
            records.append({
                "Device": args["deviceId"],
                "Action": args["action"],
                "Reason": args["reason"],
                "Dry Run": args["dryRun"],
                "Transaction": event["transactionHash"].hex()
            })

        return records, None

    except Exception as error:
        return [], str(error)

@st.fragment(run_every="5s")
def display_dashboard():

    alerts = read_csv("live_alerts.csv")
    actions = read_csv("mitigation_actions.csv")
    chain_events, error = read_blockchain()

    st.subheader("Security Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Security Alerts", len(alerts))
    c2.metric("Mitigation Decisions", len(actions))
    c3.metric("Blockchain Events", len(chain_events))

    flooding = sum(
        "FLOODING" in row.get("reasons", "").split("|")
        for row in alerts
    )

    c4.metric("Flooding Alerts", flooding)

    st.subheader("Recent AI Security Alerts")
    if alerts:
        st.dataframe(list(reversed(alerts[-20:])),
                     hide_index=True)
    else:
        st.info("No security alerts recorded yet.")

    st.subheader("Automatic Mitigation Decisions")
    st.caption("DRY_RUN: actions are logged but not enforced.")

    if actions:
        st.dataframe(list(reversed(actions[-20:])),
                     hide_index=True)
    else:
        st.info("No mitigation decisions recorded yet.")

    st.subheader("Blockchain Security Events")

    if error:
        st.warning(error)
    elif chain_events:
        st.success("Ganache blockchain connected")
        st.dataframe(list(reversed(chain_events[-20:])),
                     hide_index=True)
    else:
        st.info("No blockchain security events yet.")

display_dashboard()

@st.fragment(run_every="5s")
def display_broadband_graphs():
    import pandas as pd
    from collections import Counter

    st.divider()
    st.header("Advanced Broadband Network and Security Analytics")

    normal = read_csv("data_normal_session2.csv")
    flood = read_csv("data_flood_test.csv")

    if normal and flood:
        st.subheader("1. IoT Packet Rate Comparison")

        normal_rate = [
            float(r.get("count") or 0) / 2
            for r in normal
        ]
        flood_rate = [
            float(r.get("count") or 0) / 2
            for r in flood
        ]

        rate_df = pd.DataFrame({
            "Normal traffic": pd.Series(normal_rate),
            "Flood experiment": pd.Series(flood_rate)
        })

        st.line_chart(rate_df)
        st.caption(
            "Approximate packets per second for each "
            "2-second collection window. The two experiments "
            "were recorded separately."
        )

        st.subheader("2. Estimated IoT Application Bit Rate")

        normal_bps = [
            float(r.get("count") or 0)
            * float(r.get("mean_size") or 0)
            * 8 / 2
            for r in normal
        ]

        flood_bps = [
            float(r.get("count") or 0)
            * float(r.get("mean_size") or 0)
            * 8 / 2
            for r in flood
        ]

        bitrate_df = pd.DataFrame({
            "Normal bits/sec": pd.Series(normal_bps),
            "Flood experiment bits/sec": pd.Series(flood_bps)
        })

        st.line_chart(bitrate_df)
        st.caption(
            "Estimated IoT message bits per second. "
            "This does not measure total home broadband bandwidth."
        )

    alerts = read_csv("live_alerts.csv")

    st.subheader("3. Security Alert Breakdown")

    reasons = {
        "AI anomaly": "AI_ANOMALY",
        "Tampering": "BAD_SIGNATURE",
        "Identity spoofing": "IP_MISMATCH",
        "Flooding": "FLOODING"
    }

    if alerts:
        counts = {
            label: sum(
                code in row.get("reasons", "").split("|")
                for row in alerts
            )
            for label, code in reasons.items()
        }

        st.bar_chart(
            pd.DataFrame({
                "Attack type": list(counts.keys()),
                "Alert windows": list(counts.values())
            }).set_index("Attack type")
        )
        st.caption(
            "One alert window may contain multiple reasons."
        )
    else:
        st.info("No security alert data yet.")

    st.subheader("4. Automatic Mitigation Decisions")

    actions = read_csv("mitigation_actions.csv")

    if actions:
        counts = Counter(
            row.get("action", "UNKNOWN")
            for row in actions
        )

        st.bar_chart(
            pd.DataFrame({
                "Decision": list(counts.keys()),
                "Count": list(counts.values())
            }).set_index("Decision")
        )

        st.caption(
            "DRY_RUN decisions only. Traffic is not blocked."
        )
    else:
        st.info("No mitigation decisions recorded yet.")

    st.subheader("5. Blockchain Security Action Distribution")

    chain_events, error = read_blockchain()

    if error:
        st.warning(error)
    elif chain_events:
        counts = Counter(
            row.get("Action", "UNKNOWN")
            for row in chain_events
        )

        st.bar_chart(
            pd.DataFrame({
                "Blockchain action": list(counts.keys()),
                "Events": list(counts.values())
            }).set_index("Blockchain action")
        )
    else:
        st.info("No blockchain security events yet.")

display_broadband_graphs()

# ==========================================
# M5 - LIVE TRAFFIC AND FIREWALL ANALYTICS
# ==========================================

@st.fragment(run_every="5s")
def display_m5_analytics():
    import pandas as pd

    st.divider()
    st.header("IoT Traffic Admission and Firewall Enforcement")

    traffic = read_csv("traffic_gate_windows.csv")

    st.subheader("6. Accepted vs Rejected IoT Packets")

    if traffic:
        accepted = sum(
            int(row.get("accepted") or 0)
            for row in traffic
        )
        rejected = sum(
            int(row.get("rejected") or 0)
            for row in traffic
        )

        data = pd.DataFrame({
            "Traffic status": ["Accepted", "Rejected"],
            "Packets": [accepted, rejected]
        })

        st.bar_chart(data.set_index("Traffic status"))
        st.metric("Accepted Packets", accepted)
        st.metric("Rejected Packets", rejected)

        st.caption(
            "Cumulative application-level packet counts "
            "across recorded experiments."
        )
    else:
        st.info("No traffic admission records found.")

    st.subheader("7. Automatic Firewall Enforcement History")

    actions = read_csv("m4_enforcement.csv")

    if actions:
        st.dataframe(
            list(reversed(actions[-20:])),
            hide_index=True
        )
        st.caption(
            "These are historical enforcement records. "
            "They do not indicate whether an IP is "
            "currently blocked. Firewall blocks expire "
            "after their configured timeout."
        )
    else:
        st.info("No firewall enforcement records yet.")

display_m5_analytics()

import m5_live_status
m5_live_status.render()
