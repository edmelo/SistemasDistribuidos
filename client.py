import socket
import threading
import json
import time
import sys

class DistributedClient:
    def __init__(self, name, host='localhost', port=5000):
        self.name = name
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.client_list = []
        
    def connect(self):
        """Connect to the server"""
        try:
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to server at {self.host}:{self.port}")
            
            # Register with the server
            self.send_message({
                'type': 'register',
                'name': self.name
            })
            
            # Start a thread to receive messages
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except Exception as e:
            print(f"Error connecting to server: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the server"""
        if self.connected:
            self.connected = False
            self.client_socket.close()
            print("Disconnected from server")
    
    def send_message(self, message):
        """Send a message to the server"""
        if not self.connected:
            print("Not connected to server")
            return False
        
        try:
            message_json = json.dumps(message)
            self.client_socket.sendall(message_json.encode('utf-8'))
            return True
        except Exception as e:
            print(f"Error sending message: {e}")
            self.connected = False
            return False
    
    def broadcast_message(self, message_text):
        """Broadcast a message to all clients"""
        return self.send_message({
            'type': 'broadcast',
            'message': message_text
        })
    
    def send_direct_message(self, target, message_text):
        """Send a direct message to a specific client"""
        if target not in self.client_list:
            print(f"Unknown client: {target}")
            return False
        
        return self.send_message({
            'type': 'direct',
            'target': target,
            'message': message_text
        })
    
    def request_client_list(self):
        """Request the list of connected clients from the server"""
        return self.send_message({
            'type': 'status'
        })
    
    def receive_messages(self):
        """Receive and process messages from the server"""
        while self.connected:
            try:
                data = self.client_socket.recv(1024).decode('utf-8')
                if not data:
                    print("Connection to server lost")
                    self.connected = False
                    break
                
                message = json.loads(data)
                self.process_message(message)
            
            except json.JSONDecodeError:
                print("Received invalid message format")
            except Exception as e:
                print(f"Error receiving message: {e}")
                self.connected = False
                break
    
    def process_message(self, message):
        """Process a received message based on its type"""
        message_type = message.get('type')
        
        if message_type == 'broadcast':
            sender = message.get('sender', 'Unknown')
            msg_text = message.get('message', '')
            print(f"[Broadcast] {sender}: {msg_text}")
        
        elif message_type == 'direct':
            sender = message.get('sender', 'Unknown')
            msg_text = message.get('message', '')
            print(f"[Direct from {sender}] {msg_text}")
        
        elif message_type == 'system':
            msg_text = message.get('message', '')
            print(f"[System] {msg_text}")
        
        elif message_type == 'client_list':
            self.client_list = message.get('clients', [])
            print("Connected clients:")
            for client in self.client_list:
                print(f"- {client}")
    
    def run_interactive(self):
        """Run an interactive client session"""
        if not self.connect():
            return
        
        print("\nCommands:")
        print("  /list - Show connected clients")
        print("  /msg <client> <message> - Send a direct message to a client")
        print("  /quit - Disconnect and exit")
        print("  Any other text will be broadcast to all clients\n")
        
        try:
            while self.connected:
                user_input = input("> ")
                
                if user_input.lower() == '/quit':
                    break
                
                elif user_input.lower() == '/list':
                    self.request_client_list()
                
                elif user_input.lower().startswith('/msg '):
                    # Parse the direct message command
                    parts = user_input[5:].strip().split(' ', 1)
                    if len(parts) == 2:
                        target, message = parts
                        self.send_direct_message(target, message)
                    else:
                        print("Usage: /msg <client> <message>")
                
                elif user_input:
                    # Broadcast the message
                    self.broadcast_message(user_input)
        
        except KeyboardInterrupt:
            print("\nExiting...")
        
        finally:
            self.disconnect()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        client_name = sys.argv[1]
    else:
        client_name = input("Enter your name: ")
    
    client = DistributedClient(client_name)
    client.run_interactive()