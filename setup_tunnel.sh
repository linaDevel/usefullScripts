#!/bin/bash

SRC_IP=$(ip -4 addr show dev eno1 | grep -oP "(?<=inet ).*(?=/)")
DST_IP=${DST_IP:-$1}

if [[ -z "${DST_IP}" ]]; then
    echo "No destination IP specified"
    exit 1
fi

sudo iptables -I INPUT -p gre -s "${DST_IP}" -j ACCEPT

sudo ip link set tap0 down || true
sudo ip link del tap0 || true

sudo ip link add tap0 type gretap local "${SRC_IP}" remote "${DST_IP}"
sudo ip link set tap0 up
sudo ip link set tap0 mtu 1450

sudo brctl addbr vrouter0 || true
sudo brctl addif vrouter0 tap0 || true

echo "Execute the following commands on destination host:"
echo "sudo ip link set tap0 down"
echo "sudo ip link del tap0"
echo "sudo ip link add tap0 type gretap local \"${DST_IP}\" remote \"${SRC_IP}\""
echo "sudo ip link set tap0 up"
echo "sudo ip link set tap0 mtu 1450"
echo "sudo brctl addbr vrouter0"
echo "sudo brctl addif vrouter0 tap0"
echo "sudo iptables -I INPUT -p gre -s \"${SRC_IP}\" -j ACCEPT"
echo "sudo dhclient vrouter0"
