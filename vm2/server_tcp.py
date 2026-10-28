import socket
import json

def run_tcp_server(host, port):
    # socket IPv4 TCP creation
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #to reuse por after restart 

        try:
            s.bind((host, port)) #association between serer network interface and tcp port
            s.listen()#socket listening waiting for connection requests
            print(f"[*] TCP Legacy Server listening on {host}:{port}...")
            
            while True:
                conn, addr = s.accept() #server waits the tcp syn
                with conn: #the connection closes when the block ends
                    try:    
                        data = conn.recv(1024) #reads 1024 bytes from buffer
                        if data:
                            payload = json.loads(data.decode('utf-8'))
                            print(f"\n[ TCP ALERT] from {payload.get('sensor_id')}")
                            print(f"   Temp:   {payload.get('temperature')}°C | Smoke: {payload.get('smoke_level')}%")
                    except json.JSONDecodeError:
                        print(
                            f"[!] Received malformed JSON from {addr[0]}, ignoring packet."
                        )
                    except Exception as e:
                        print(f"[!] Error processing request: {e}")

        except KeyboardInterrupt:
            print("\n[*] Server shutdown by user.")

if __name__ == "__main__":
    run_tcp_server("10.0.1.1", 4434)
