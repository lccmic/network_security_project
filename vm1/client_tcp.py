import socket
import json
import random
import time
from datetime import datetime

TEMP_THRESHOLD = 60.0 #temperature threshold
SMOKE_THRESHOLD = 80.0 #smoke treshold

def run_tcp_sensor(host, port, num_logs):
    print(f"\nStarting TCP simulation of {num_logs} logs...")

    for i in range(num_logs):
        #creation of random values for temperature and smoke
        temp = round(random.uniform(20.0, 85.0), 2)
        smoke = round(random.uniform(0.0, 100.0), 2)

        print(f"[{i+1}/{num_logs}] TCP Reading: Temp={temp}°C, Smoke={smoke}% ", end="")

        if temp > TEMP_THRESHOLD or smoke > SMOKE_THRESHOLD:
            print("-> SENDING ALERT...")

            #creation of json payload to send
            payload = {
                "sensor_id": "SENS-FIRE-01",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "FIRE_ALARM",
                "temperature": temp,
                "smoke_level": smoke,
                "status": "CRITICAL"
            }
            
            data = json.dumps(payload).encode('utf-8')

            try:
                #open TCP connection
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s: #socket tcp ipv4 declaration
                    #TIMER 1: START CONNECTION SETUP (3-way handshake)
                    conn_start = time.perf_counter()
                    s.connect((host, port)) #wait until 3way handshake is completed
                    
                    #TIMER 1: STOP CONNECTION SETUP
                    conn_end = time.perf_counter()
                    elapsed_conn_ms = (conn_end - conn_start) * 1000
                    print(f"    [*] TCP Connection established in {elapsed_conn_ms:.2f} ms (3-way handshake)")

                    #TIMER 2: START TRANSMISSION
                    tx_start = time.perf_counter()
                    
                    s.sendall(data)#send all bytes to the network socket
                    
                    #TIMER 2: STOP TRANSMISSION
                    tx_end = time.perf_counter()
                    elapsed_tx_ms = (tx_end - tx_start) * 1000
                    print(f"    [!] Alert transmitted in {elapsed_tx_ms:.2f} ms")
                    
                    #print total time
                    total_ms = elapsed_conn_ms + elapsed_tx_ms
                    print(f"    [=] Total Time-to-Alert: {total_ms:.2f} ms\n")
            except socket.timeout:
                print(
                    "    [X] ERROR: Connection timeout. Server non raggiungibile o firewall attivo.\n"
                )
            except socket.error as e:
                print(f"    [X] ERROR: Socket error ({e})\n")

        else:
            print("-> Normal.")

        time.sleep(1)

if __name__ == "__main__":
    try:
        n = int(input("How many logs for TCP? "))
        run_tcp_sensor("10.0.1.1", 4434, n)
    except ValueError:
        print("error: Invalid number.")