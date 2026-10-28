import asyncio
import json
import random
import time
from datetime import datetime
import ssl
from aioquic.asyncio import connect
from aioquic.quic.configuration import QuicConfiguration

# emergency thresholds for temperature and smoke levels
TEMP_THRESHOLD = 60.0
SMOKE_THRESHOLD = 80.0

async def run_sensor(host, port, num_logs):
    #create the configuration for the quic client specifying that it is a client and disabling certificate verification since it is a selfsigned certificate for lab
    configuration = QuicConfiguration(is_client=True, verify_mode=ssl.CERT_NONE)

    print(f"\nStarting simulation of {num_logs} ambiental logs...")

    # timer 1: start connection setup
    conn_start = time.perf_counter()

    async with connect(host, port, configuration=configuration) as protocol: #start quic handshake
        
        #timer 1 stop connection setup
        conn_end = time.perf_counter()
        elapsed_conn_ms = (conn_end - conn_start) * 1000
        print(f"\n[*] QUIC Connection established in {elapsed_conn_ms:.2f} ms (1-RTT/TLS 1.3)")

        for i in range(num_logs):
            # Generate random sensor data
            temp = round(random.uniform(20.0, 85.0), 2)
            smoke = round(random.uniform(0.0, 100.0), 2)
            
            print(f"[{i+1}/{num_logs}] Reading: Temp={temp}°C, Smoke={smoke}% ", end="")
            
            if temp > TEMP_THRESHOLD or smoke > SMOKE_THRESHOLD:
                print("!CRITICAL THRESHOLD REACHED! Sending alert...")
                
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                alert_payload = {
                    "sensor_id": "SENS-FIRE-01", 
                    "timestamp": current_time,   
                    "type": "FIRE_ALARM",        
                    "temperature": temp,         
                    "smoke_level": smoke,        
                    "status": "CRITICAL"
                }
                
                data = json.dumps(alert_payload).encode('utf-8')
                
                #TIMER 2 start transmission
                tx_start = time.perf_counter()

                stream_id = protocol._quic.get_next_available_stream_id()#assign a new stream id 
                protocol._quic.send_stream_data(stream_id, data, end_stream=True)#write bytes on the stream buffer and sets the fin flag
                protocol.transmit()#send data

                #TIMER 2 stop transmission
                tx_end = time.perf_counter()
                elapsed_tx_ms = (tx_end - tx_start) * 1000
                print(f"    [!] Alert transmitted via QUIC stream in {elapsed_tx_ms:.2f} ms")
            else:
                print("Normal conditions.")

            await asyncio.sleep(1)

    print("\nSimulation complete. Connection closed.")

if __name__ == "__main__":
    try:
        n = int(input("How many logs do you want to simulate? "))
        asyncio.run(run_sensor("10.0.1.1", 4433, n))
    except ValueError:
        print("error: Please enter a valid integer for the number of logs.")
    except Exception as e:
        print(f"Connection error: {e}")