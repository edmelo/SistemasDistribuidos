import socket
import threading
import json
import time
import sys
import random

class DistributedTaskWorker:
    def __init__(self, name, host='localhost', port=5000):
        self.name = name
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.client_list = []
        self.processing = False
        
    def connect(self):
        """Connect to the server"""
        try:
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            print(f"Worker {self.name} connected to server at {self.host}:{self.port}")
            
            # Register with the server
            self.send_message({
                'type': 'register',
                'name': f"Worker-{self.name}"
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
            print(f"Worker {self.name} disconnected from server")
    
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
    
    def broadcast_status(self, status):
        """Broadcast worker status to all clients"""
        return self.send_message({
            'type': 'broadcast',
            'message': f"Worker status: {status}"
        })
    
    def process_task(self, task_data, task_id, requester):
        """Process a task and return the result"""
        self.processing = True
        print(f"Processing task {task_id} from {requester}...")
        
        # Simulate task processing with a delay
        processing_time = random.uniform(1, 5)
        time.sleep(processing_time)
        
        # Simple task processing logic
        try:
            # For demonstration, we'll just perform some basic operations based on task_type
            task_type = task_data.get('task_type', 'unknown')
            task_params = task_data.get('params', {})
            
            result = None
            if task_type == 'calculate':
                operation = task_params.get('operation')
                numbers = task_params.get('numbers', [])
                
                if operation == 'sum':
                    result = sum(numbers)
                elif operation == 'average':
                    result = sum(numbers) / len(numbers) if numbers else 0
                elif operation == 'max':
                    result = max(numbers) if numbers else None
                elif operation == 'min':
                    result = min(numbers) if numbers else None
            
            elif task_type == 'process_text':
                text = task_params.get('text', '')
                operation = task_params.get('operation')
                
                if operation == 'count_words':
                    result = len(text.split())
                elif operation == 'count_chars':
                    result = len(text)
                elif operation == 'uppercase':
                    result = text.upper()
                elif operation == 'lowercase':
                    result = text.lower()
            
            # Send the result back to the requester
            self.send_message({
                'type': 'direct',
                'target': requester,
                'message': f"Task {task_id} completed in {processing_time:.2f}s",
                'task_result': {
                    'task_id': task_id,
                    'result': result,
                    'processing_time': processing_time
                }
            })
            
            print(f"Task {task_id} completed. Result: {result}")
        
        except Exception as e:
            print(f"Error processing task: {e}")
            # Notify the requester about the error
            self.send_message({
                'type': 'direct',
                'target': requester,
                'message': f"Error processing task {task_id}: {str(e)}",
                'task_result': {
                    'task_id': task_id,
                    'error': str(e)
                }
            })
        
        finally:
            self.processing = False
    
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
            
            # Check if this is a task request
            task_data = message.get('task_data')
            task_id = message.get('task_id')
            
            if task_data and task_id and not self.processing:
                # Process the task in a separate thread
                task_thread = threading.Thread(
                    target=self.process_task,
                    args=(task_data, task_id, sender)
                )
                task_thread.daemon = True
                task_thread.start()
            else:
                print(f"[Direct from {sender}] {msg_text}")
        
        elif message_type == 'system':
            msg_text = message.get('message', '')
            print(f"[System] {msg_text}")
        
        elif message_type == 'client_list':
            self.client_list = message.get('clients', [])
    
    def run(self):
        """Run the worker"""
        if not self.connect():
            return
        
        print(f"Worker {self.name} is running and waiting for tasks...")
        self.broadcast_status("ready for tasks")
        
        try:
            # Keep the worker running
            while self.connected:
                time.sleep(1)
        
        except KeyboardInterrupt:
            print("\nWorker shutting down...")
        
        finally:
            self.disconnect()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        worker_name = sys.argv[1]
    else:
        worker_name = f"Worker-{random.randint(1000, 9999)}"
    
    worker = DistributedTaskWorker(worker_name)
    worker.run()