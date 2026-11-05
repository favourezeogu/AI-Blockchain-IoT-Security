
# AI and Blockchain-Secured IoT Broadband Network

## Project Overview

This project implements a closed-loop IoT cybersecurity
prototype using Artificial Intelligence, blockchain,
and automatic network-level mitigation.

The system detects malicious IoT activity over a home
broadband/Wi-Fi network, enforces temporary firewall
restrictions, records security events on a private
Ethereum blockchain, and displays results through
a Streamlit dashboard.

## Technologies

- Raspberry Pi 5
- Ubuntu Linux
- Python and scikit-learn
- Isolation Forest anomaly detection
- HMAC-SHA256 authentication
- Solidity smart contracts
- Ganache and Truffle
- Web3.py
- nftables firewall
- Streamlit dashboard

## Security Capabilities

1. AI anomaly detection
2. Packet authentication
3. Device identity-spoofing detection
4. Flooding detection
5. Blockchain-based device authorization
6. Automatic temporary UDP blocking
7. Blockchain mitigation-event logging
8. Live security monitoring

## Performance Results

Four controlled enforcement experiments were conducted.

- Average firewall-helper execution time: 35.654 ms
- Average blockchain confirmation time: 216.317 ms
- Confirmed blockchain transactions: 4 out of 4 trials

These figures represent processing stages after attack
detection, not complete end-to-end packet detection latency.

## Reproduction Notes

Create edge/config.py from edge/config.example.py
and replace the example authentication keys and IP
addresses with values appropriate for your own
laboratory environment.

The implementation uses a local Ganache blockchain
and Linux nftables firewall rules.

## Project Status

Core implementation and controlled experimental tests
completed in November 2026.

## Academic Context

Advanced Broadband Communication Systems
Prairie View A&M University
Fall 2026
