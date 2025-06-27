import socket
import threading
import json
import time
from db_manager import DatabaseManager

class DistributedServer:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = {}  # Dictionary to store client connections
        self.client_names = {}  # Dictionary to map client addresses to names
        self.lock = threading.Lock()  # Lock for thread-safe operations
        self.db = DatabaseManager()  # Database manager for persistence

    def start(self):
        """Start the server and listen for connections"""
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")

        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"New connection from {client_address}")

                # Start a new thread to handle the client
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("Server shutting down...")
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket, client_address):
        """Handle communication with a client"""
        client_name = None
        try:
            # Register the client in memory
            with self.lock:
                self.clients[client_address] = client_socket

            # First message should be the client's name
            name_data = client_socket.recv(1024).decode('utf-8')
            try:
                name_msg = json.loads(name_data)
                if name_msg.get('type') == 'register':
                    client_name = name_msg.get('name', f"Client-{client_address[1]}")
                    with self.lock:
                        self.client_names[client_address] = client_name

                    # Determine client type based on name prefix
                    client_type = "regular"
                    if client_name.startswith("Worker-"):
                        client_type = "worker"
                    elif client_name.startswith("TaskClient-"):
                        client_type = "task_client"

                    # Register client in database
                    self.db.register_client(client_name, client_type)

                    # Store system message in database
                    system_message = f"{client_name} joined the system"
                    self.db.store_message("system", "Server", system_message)

                    # Notify all clients about the new client
                    self.broadcast({
                        'type': 'system',
                        'message': system_message,
                        'timestamp': time.time()
                    }, exclude=None)

                    # Send the list of connected clients to the new client
                    self.send_client_list(client_socket)
            except json.JSONDecodeError:
                print(f"Invalid registration message from {client_address}")

            # Handle client messages
            while True:
                data = client_socket.recv(1024).decode('utf-8')
                if not data:
                    break

                try:
                    message = json.loads(data)
                    message_type = message.get('type')

                    if message_type == 'broadcast':
                        # Add sender information and broadcast to all clients
                        sender = self.client_names.get(client_address, f"Client-{client_address[1]}")
                        message['sender'] = sender
                        message['timestamp'] = time.time()

                        # Store message in database
                        self.db.store_message("broadcast", sender, message.get('message', ''))

                        # Broadcast to all clients
                        self.broadcast(message, exclude=None)

                    elif message_type == 'direct':
                        # Direct message to a specific client
                        target = message.get('target')
                        sender = self.client_names.get(client_address, f"Client-{client_address[1]}")
                        message['sender'] = sender
                        message['timestamp'] = time.time()

                        # Check if this is a task submission
                        if 'task_data' in message and 'task_id' in message:
                            # Store task in database
                            task_data = message.get('task_data', {})
                            task_id = message.get('task_id')
                            task_type = task_data.get('task_type', 'unknown')
                            params = task_data.get('params', {})

                            self.db.store_task(task_id, task_type, target, sender, params)

                        # Store message in database
                        self.db.store_message("direct", sender, message.get('message', ''), target)

                        # Send direct message
                        self.send_direct_message(message, target)

                    elif message_type == 'status':
                        # Send the list of connected clients
                        self.send_client_list(client_socket)

                    # Check if this is a task result
                    if 'task_result' in message:
                        task_result = message.get('task_result')
                        task_id = task_result.get('task_id')

                        # Update task result in database
                        self.db.update_task_result(task_id, task_result)

                except json.JSONDecodeError:
                    print(f"Invalid message format from {client_address}")

        except Exception as e:
            print(f"Error handling client {client_address}: {e}")

        finally:
            # Clean up when client disconnects
            with self.lock:
                if client_address in self.clients:
                    client_name = self.client_names.get(client_address, f"Client-{client_address[1]}")
                    del self.clients[client_address]
                    if client_address in self.client_names:
                        del self.client_names[client_address]

                    # Update client status in database
                    if client_name:
                        self.db.disconnect_client(client_name)

                    # Store system message in database
                    system_message = f"{client_name} left the system"
                    self.db.store_message("system", "Server", system_message)

                    # Notify all clients about the disconnection
                    self.broadcast({
                        'type': 'system',
                        'message': system_message,
                        'timestamp': time.time()
                    }, exclude=None)

            client_socket.close()
            print(f"Connection closed with {client_address}")

    def broadcast(self, message, exclude=None):
        """Send a message to all connected clients except the excluded one"""
        message_json = json.dumps(message)

        with self.lock:
            for addr, client in self.clients.items():
                if exclude is None or addr != exclude:
                    try:
                        client.sendall(message_json.encode('utf-8'))
                    except:
                        # If sending fails, the client will be removed in the handle_client method
                        pass

    def send_direct_message(self, message, target):
        """Send a message to a specific client by name"""
        message_json = json.dumps(message)

        with self.lock:
            target_address = None
            for addr, name in self.client_names.items():
                if name == target:
                    target_address = addr
                    break

            if target_address and target_address in self.clients:
                try:
                    self.clients[target_address].sendall(message_json.encode('utf-8'))
                except:
                    # If sending fails, the client will be removed in the handle_client method
                    pass

    def send_client_list(self, client_socket):
        """Send the list of connected clients to a client"""
        with self.lock:
            client_list = list(self.client_names.values())

        message = {
            'type': 'client_list',
            'clients': client_list,
            'timestamp': time.time()
        }

        try:
            client_socket.sendall(json.dumps(message).encode('utf-8'))
        except:
            # If sending fails, the client will be removed in the handle_client method
            pass

if __name__ == "__main__":
    server = DistributedServer()
    server.start()
