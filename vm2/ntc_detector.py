import os
import subprocess
import time
import pandas as pd

# NTC Configurations
INTERFACE = "enp0s3"
PORT = "4433"
PACKETS_TO_SNIFF = 300
DOS_THRESHOLD = 60  #Percentage threshold for DoS classification
BLOCKED_IPS = set()


def print_dashboard(ip_counts):
    os.system("clear")
    print("=" * 70)
    print(" NTC LIVE TRAFFIC MONITOR & DoS MITIGATION SYSTEM")
    print("=" * 70)
    print(f"Target Port : {PORT} UDP / ESP")
    print(f"Window Size : {PACKETS_TO_SNIFF} packets")
    print(f"Threshold   : {DOS_THRESHOLD}% from a single IP")
    print(
        f"Blocked IPs : {', '.join(BLOCKED_IPS) if BLOCKED_IPS else 'None'}"
    )
    print("-" * 70)

    if ip_counts.empty:
        print("[Info] Waiting for traffic... capturing packets...")
        print("=" * 70)
        return

    print(f"{'SOURCE IP':<16} | {'PACKETS':<8} | {'PERCENTAGE':<12} | {'STATUS'}")
    print("-" * 70)

    for ip, count in ip_counts.items():
        percent = (count / PACKETS_TO_SNIFF) * 100

        if ip in BLOCKED_IPS:
            status = "[BLOCKED]"
        elif percent >= DOS_THRESHOLD:
            status = "!!![ATTACK DETECTED]!!!"
        else:
            status = "[NORMAL]"

        print(f"{ip:<16} | {count:<8} | {percent:>5.1f}%      | {status}")
        print("=" * 70)


def analyze_live_traffic():
    # Capture 300 packets using tcpdump
    cmd = f"sudo tcpdump -c {PACKETS_TO_SNIFF} -i {INTERFACE} -n 'esp or (udp port {PORT})' 2>/dev/null | awk '{{print $3}}'"

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True
        )
        raw_lines = result.stdout.strip().split("\n")
    except Exception as e:
        print(f"[-] Error during packet capture: {e}")
        return

    cleaned_ips = []
    for line in raw_lines:
        line = line.strip()
        if line:
            # Extract pure IPv4 address (stripping ports or trailing characters)
            ip_parts = line.split(".")
            if len(ip_parts) >= 4:
                pure_ip = ".".join(ip_parts[:4])
                cleaned_ips.append(pure_ip)

    if cleaned_ips:
        df = pd.DataFrame(cleaned_ips, columns=["source_ip"])
        ip_counts = df["source_ip"].value_counts()
    else:
        ip_counts = pd.Series(dtype=int)

    print_dashboard(ip_counts)

    # Mitigation logic
    for ip, count in ip_counts.items():
        percent = (count / PACKETS_TO_SNIFF) * 100
        if percent >= DOS_THRESHOLD and ip not in BLOCKED_IPS:
            print(f"\n[!] INITIATING MITIGATION PROTOCOL FOR {ip}...")
            time.sleep(1)

            #High priority stateless drop rule injection
            block_cmd = f"sudo iptables -I INPUT 1 -s {ip} -j DROP"
            subprocess.run(block_cmd, shell=True)

            BLOCKED_IPS.add(ip)
            print(
                f"[+] {ip} successfully blocked at kernel level (iptables Position 1)."
            )
            time.sleep(2)


if __name__ == "__main__":
    try:
        while True:
            analyze_live_traffic()
    except KeyboardInterrupt:
        print("\n[*] NTC shutdown by user.")
    finally:
        print("\n[*] Performing automated cleanup of Firewall rules...")
        for ip in list(BLOCKED_IPS):
            subprocess.run(
                f"sudo iptables -D INPUT -s {ip} -j DROP", shell=True
            )
            print(f"    -> Removed DROP rule for {ip}")
        print("[+] Environment restored to normal posture.")