import socket
import threading
import json
import time
import sys
import uuid

class DistributedTaskClient:
    def __init__(self, name, host='localhost', port=5000):
        self.name = name
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.client_list = []
        self.task_results = {}
        self.tasks_pending = {}
        
    def connect(self):
        """Connect to the server"""
        try:
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            print(f"Task Client {self.name} connected to server at {self.host}:{self.port}")
            
            # Register with the server
            self.send_message({
                'type': 'register',
                'name': f"TaskClient-{self.name}"
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
            print(f"Task Client {self.name} disconnected from server")
    
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
    
    def request_client_list(self):
        """Request the list of connected clients from the server"""
        return self.send_message({
            'type': 'status'
        })
    
    def submit_task(self, worker, task_type, params):
        """Submit a task to a worker"""
        if not worker.startswith("Worker-"):
            print("Invalid worker name. Worker names should start with 'Worker-'")
            return None
        
        if worker not in self.client_list:
            print(f"Worker {worker} not found in the client list")
            return None
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # Create the task message
        task_message = {
            'type': 'direct',
            'target': worker,
            'message': f"New task: {task_type}",
            'task_data': {
                'task_type': task_type,
                'params': params
            },
            'task_id': task_id
        }
        
        # Store the task in pending tasks
        self.tasks_pending[task_id] = {
            'worker': worker,
            'task_type': task_type,
            'params': params,
            'submit_time': time.time()
        }
        
        # Send the task
        if self.send_message(task_message):
            print(f"Task {task_id} submitted to {worker}")
            return task_id
        else:
            print(f"Failed to submit task to {worker}")
            del self.tasks_pending[task_id]
            return None
    
    def get_task_result(self, task_id, timeout=None):
        """Get the result of a task, optionally waiting for it to complete"""
        if task_id in self.task_results:
            # Task already completed
            return self.task_results[task_id]
        
        if task_id not in self.tasks_pending:
            # Task not found
            return None
        
        if timeout is not None:
            # Wait for the task to complete with timeout
            start_time = time.time()
            while time.time() - start_time < timeout:
                if task_id in self.task_results:
                    return self.task_results[task_id]
                time.sleep(0.1)
            
            # Timeout reached
            return None
        
        # Task is still pending
        return None
    
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
        
        if message_type == 'direct':
            sender = message.get('sender', 'Unknown')
            msg_text = message.get('message', '')
            
            # Check if this is a task result
            task_result = message.get('task_result')
            if task_result:
                task_id = task_result.get('task_id')
                if task_id in self.tasks_pending:
                    # Store the result
                    self.task_results[task_id] = task_result
                    # Remove from pending tasks
                    task_info = self.tasks_pending.pop(task_id)
                    
                    # Calculate task duration
                    submit_time = task_info.get('submit_time', 0)
                    duration = time.time() - submit_time
                    
                    print(f"Task {task_id} completed by {sender} in {duration:.2f}s")
                    print(f"Result: {task_result.get('result')}")
            else:
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
        """Run an interactive task client session"""
        if not self.connect():
            return
        
        print("\nCommands:")
        print("  /list - Show connected clients")
        print("  /workers - Show available workers")
        print("  /calculate <worker> <operation> <numbers> - Submit a calculation task")
        print("  /text <worker> <operation> <text> - Submit a text processing task")
        print("  /results - Show task results")
        print("  /quit - Disconnect and exit")
        
        try:
            while self.connected:
                user_input = input("> ")
                
                if user_input.lower() == '/quit':
                    break
                
                elif user_input.lower() == '/list':
                    self.request_client_list()
                
                elif user_input.lower() == '/workers':
                    workers = [c for c in self.client_list if c.startswith("Worker-")]
                    if workers:
                        print("Available workers:")
                        for worker in workers:
                            print(f"- {worker}")
                    else:
                        print("No workers available")
                
                elif user_input.lower().startswith('/calculate '):
                    # Parse the calculate command
                    parts = user_input[11:].strip().split(' ', 2)
                    if len(parts) == 3:
                        worker, operation, numbers_str = parts
                        try:
                            numbers = [float(n) for n in numbers_str.split()]
                            self.submit_task(worker, 'calculate', {
                                'operation': operation,
                                'numbers': numbers
                            })
                        except ValueError:
                            print("Invalid numbers format. Use space-separated numbers.")
                    else:
                        print("Usage: /calculate <worker> <operation> <numbers>")
                        print("Operations: sum, average, max, min")
                
                elif user_input.lower().startswith('/text '):
                    # Parse the text processing command
                    parts = user_input[6:].strip().split(' ', 2)
                    if len(parts) == 3:
                        worker, operation, text = parts
                        self.submit_task(worker, 'process_text', {
                            'operation': operation,
                            'text': text
                        })
                    else:
                        print("Usage: /text <worker> <operation> <text>")
                        print("Operations: count_words, count_chars, uppercase, lowercase")
                
                elif user_input.lower() == '/results':
                    if self.task_results:
                        print("Task results:")
                        for task_id, result in self.task_results.items():
                            print(f"Task {task_id}: {result}")
                    else:
                        print("No task results available")
        
        except KeyboardInterrupt:
            print("\nExiting...")
        
        finally:
            self.disconnect()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        client_name = sys.argv[1]
    else:
        client_name = input("Enter your name: ")
    
    client = DistributedTaskClient(client_name)
    client.run_interactive()