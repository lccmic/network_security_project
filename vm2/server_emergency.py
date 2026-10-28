import asyncio
import json
from aioquic.asyncio import serve, QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived

class EmergencyServerProtocol(QuicConnectionProtocol):
    #function to handle incoming QUIC events
    def quic_event_received(self, event): #callback invoked by aioquic to manage state machine of a quic connection
        #check if the event is received stream data
        if isinstance(event, StreamDataReceived):#filter events where a client frame is sent on a stream
            try:
                #decode the received data and parse it as JSON
                data = event.data.decode('utf-8') #raw data received from the client are decoded from bytes to string
                alert = json.loads(data) #transform the string into a JSON object
                print(f"+++ALERT RECEIVED: {alert}+++")
            except Exception as e:
                print(f"[Error]: {e}")

async def main():
    configuration = QuicConfiguration(is_client=False) #create the configuration for the QUIC server, specifying that it is not a client
    configuration.load_cert_chain("server.crt", "server.key") #load the server certificate and private key generated through openssl 

    print("QUIC Server listening on 10.0.1.1:4433")
    #start the quic server and listen for incoming connections
    await serve("10.0.1.1", 4433, configuration=configuration, create_protocol=EmergencyServerProtocol) #create upd socket

    await asyncio.Future() #keep the server running indefinitely


if __name__ == "__main__":
    try:
    #start the asyncio event loop to start the quic server
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[*] Server shutdown by user.")
