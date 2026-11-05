
#!/bin/sh
set -eu

# Advanced Broadband Communications Project
# M5 - Read current firewall status

# Display currently blocked IoT device IP addresses
# This does not block or unblock any device.

exec /usr/sbin/nft -j list set inet iot_m4 blocked_ipv4
