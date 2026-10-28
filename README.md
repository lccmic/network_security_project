# Secure Network Architecture for Critical IoT Systems: A QUIC and IPsec Implementation

**Network Security Project**

*Lecca Michela*

## Abstract
This project implements a simulated secure, low-latency network infrastructure for a mission-critical IoT fire alert system.
The project compares **QUIC (UDP)** over legacy **TCP**, uses **IPsec (ESP in Transport Mode)** for payload confidentiality a **firewall** for perimeter hardening and implements a custom Python **Network Traffic Classifier (NTC)** to detect and mitigate volumetric DoS attacks autonomously.

## Structure
**VM1 (IoT Sensor Client):** `10.0.1.2` :IoT Telemetry Publisher & DoS Flood Generator

* `client_sensor.py`: Asynchronous QUIC telemetry publisher (aioquic)
* `client_tcp.py`: Legacy TCP control baseline publisher
* `client_flood.py`: Volumetric UDP flood generator for DoS testing
* `firewall_rules.txt` :Saved iptables policy configuration 
* `ipsec_setup.sh `: Shell script to inject kernel ipsec XFRM SAs and SPs
* `remove_ipsec.sh`: Shell script to flush kernel IPsec policies

**VM2 (Emergency Server):** `10.0.1.1`: QUIC/TCP Receiver, Firewall & NTC Detector
* `server_emergency.py`: Asynchronous QUIC emergency alert listener (Port 4433)
* `server_tcp.py`: Legacy TCP receiver listener (Port 4434)
* `ntc_detector.py`: Real-time traffic analyzer / automated firewall mitigator
* `firewall_rules.txt` :Saved iptables policy configuration 
* `ipsec_setup.sh `: Shell script to inject kernel ipsec XFRM SAs and SPs
* `remove_ipsec.sh`: Shell script to flush kernel IPsec policies




## Prerequisites
* 2x Ubuntu Server VMs connected via VirtualBox Internal Network
* Python 3.10+, pip, tcpdump, tshark, iptables, net-tools.


## Installation & Setup

**1. Install Dependencies (On both VMs):**
```bash
sudo apt update
sudo apt install -y python3 python3-pip tcpdump tshark iptables net-tools
pip3 install aioquic pandas
```

**2. Generate TLS Certificates (On Server VM2):**
```bash
openssl req -x509 -newkey rsa:2048 -keyout server.key -out server.crt -days 365 -nodes -subj "/CN=10.0.1.1"
```

**3. Configure Firewall & IPsec**
```bash
sudo iptables-restore < firewall_rules.txt
sudo chmod +x setup_ipsec.sh
sudo ./setup_ipsec.sh
```

## How to Run

### 1. Legacy TCP Test (Latency Comparison)
* **Server:** Start the tcp server: `python3 server_tcp.py`
* **Client:** Send the sensor data through tcp `python3 client_tcp.py`

### 2. Secure QUIC Infrastructure
* **Server:** Start the quic server `python3 server_emergency.py`
* **Client:** Send the sensor data `python3 client_sensor.py`

*(Check `tshark -i enp0s3 -Y "esp"` to verify ESP encapsulation)*

### 3. DoS Attack & NTC Mitigation
* **Server (Terminal 1):** Start the QUIC Server (`python3 server_emergency.py`)
* **Server (Terminal 2):** Start the NTC Defense (`sudo python3 ntc_detector.py`)
* **Client:** Launch the attack (`python3 client_flood.py`)

###
To flush IPsec SAs and restore native networking:
```bash
sudo ./remove_ipsec.sh
```
