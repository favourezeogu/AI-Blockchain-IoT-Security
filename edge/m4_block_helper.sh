
#!/bin/sh
set -eu

# Raspberry Pi IP for the controlled class demonstration
PI_IP="192.168.1.179"

# Block only this device's UDP traffic to port 5005
# The nftables set automatically expires after 30 seconds

exec /usr/sbin/nft add element inet iot_m4 blocked_ipv4 \
    "{ $PI_IP timeout 30s }"
