# SDN-Based Firewall using Mininet + POX

**Course:** COMPUTER NETWORKS — UE24CS252B
**Project:** SDN Mininet Simulation — Problem 2: SDN-Based Firewall
**Controller:** POX (OpenFlow 1.0)
**Emulator:** Mininet

---

## 1. Problem Statement

Develop a controller-based firewall to block or allow traffic between hosts using:
- Rule-based filtering (IP-based)
- Install drop rules on the switch via OpenFlow
- Test allowed vs blocked traffic
- Maintain logs of blocked packets in the controller console

---

## 2. Topology
h1 (10.0.0.1)       h2 (10.0.0.2)
          \                   /
           \                 /
            +------[s1]------+
                    |
                    |
            h3 (10.0.0.3)
- **s1** — Open vSwitch (OpenFlow 1.0)
- **h1** — Trusted Host A (10.0.0.1)
- **h2** — Trusted Host B (10.0.0.2)
- **h3** — Untrusted/Blocked Host (10.0.0.3)
- **Controller** — POX running on 127.0.0.1:6633

---

## 3. Firewall Rules

| Rule | Source IP | Destination IP | Action |
|------|-----------|----------------|--------|
| 1 | 10.0.0.1 (h1) | 10.0.0.3 (h3) | BLOCK |
| 2 | 10.0.0.3 (h3) | 10.0.0.1 (h1) | BLOCK |
| Default | Any | Any | ALLOW |

---

## 4. SDN Logic and Flow Rule Design

The controller logic follows the Match-Action model:

1. Switch Handshake — When the switch connects, the controller immediately installs DROP flow rules for blocked IP pairs using ofp_flow_mod with an empty action list.

2. Match Fields Used:
   - dl_type = IPv4
   - nw_src = Source IP
   - nw_dst = Destination IP

3. Priority Scheme:

| Priority | Purpose |
|----------|---------|
| 20 | DROP rule for blocked traffic |
| Default | L2 learning switch (forwarding) |

4. Logging — Every blocked packet that reaches the controller triggers a log.warning entry showing source and destination IP.

---

## 5. Setup and Installation

### Prerequisites

    sudo apt update && sudo apt upgrade -y
    sudo apt install mininet -y
    cd ~
    git clone https://github.com/noxrepo/pox.git

### Install Firewall Controller

    cp sdn_firewall.py ~/pox/ext/

---

## 6. Execution Steps

### Terminal 1 — Start POX Controller

    cd ~/pox
    ./pox.py log.level --DEBUG forwarding.l2_learning sdn_firewall

Expected output:

    INFO:sdn_firewall:SDN Firewall Controller Started
    INFO:sdn_firewall:Blocking h1(10.0.0.1) <-> h3(10.0.0.3)
    INFO:sdn_firewall:Switch connected: 1
    INFO:sdn_firewall:DROP rule installed: 10.0.0.1 -> 10.0.0.3
    INFO:sdn_firewall:DROP rule installed: 10.0.0.3 -> 10.0.0.1

### Terminal 2 — Start Mininet

    sudo mn -c
    sudo mn --topo single,3 --controller remote,ip=127.0.0.1,port=6633

---

## 7. Test Scenarios

### Scenario 1 — Allowed vs Blocked (ping)

    mininet> h1 ping -c 5 h2

Expected: 0% packet loss (ALLOWED)

    mininet> h1 ping -c 5 h3

Expected: 100% packet loss (BLOCKED)

### Scenario 2 — Flow Table Verification

    mininet> sh ovs-ofctl dump-flows s1

Expected:

    priority=20, ip, nw_src=10.0.0.1, nw_dst=10.0.0.3  actions=drop
    priority=20, ip, nw_src=10.0.0.3, nw_dst=10.0.0.1  actions=drop

### Scenario 3 — Throughput (iperf)

    mininet> h2 iperf -s &
    mininet> h1 iperf -c 10.0.0.2 -t 10

Measures bandwidth between allowed hosts h1 and h2.

### Scenario 4 — Topology Info

    mininet> nodes
    mininet> net

---

## 8. Expected Output

### Ping Results
- h1 to h2 : 0% loss (Allowed)
- h1 to h3 : 100% loss (Blocked by Firewall)

### Controller Log

    INFO:  SDN Firewall Controller Started
    INFO:  DROP rule installed: 10.0.0.1 -> 10.0.0.3
    INFO:  DROP rule installed: 10.0.0.3 -> 10.0.0.1
    WARNING: BLOCKED PACKET: 10.0.0.1 -> 10.0.0.3

### Flow Table

    cookie=0x0, duration=10s, priority=20,
    ip,nw_src=10.0.0.1,nw_dst=10.0.0.3 actions=drop

    cookie=0x0, duration=10s, priority=20,
    ip,nw_src=10.0.0.3,nw_dst=10.0.0.1 actions=drop

---

## 9. Cleanup

    mininet> exit
    Ctrl + C
    sudo mn -c

---

## 10. Project Structure

    SDN-BASED-FIREWALL/
    ├── src/
    │   └── sdn_firewall.py       # POX controller firewall logic
    ├── screenshots/
    │   ├── ping_results.png      # Allowed vs blocked ping test
    │   ├── flow_table.png        # OVS flow table with drop rules
    │   ├── controller_logs.png   # POX terminal showing blocked logs
    │   ├── iperf_results.png     # Throughput measurement
    │   └── topology.png          # nodes and net output
    └── README.md

---

## 11. References

1. POX Controller Documentation — https://github.com/noxrepo/pox
2. Mininet Walkthrough — https://mininet.org/walkthrough/
3. OpenFlow 1.0 Specification — https://opennetworking.org
4. Open vSwitch — https://www.openvswitch.org
5. Mininet GitHub — https://github.com/mininet/mininet
