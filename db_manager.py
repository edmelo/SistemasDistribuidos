import sqlite3
import json
import time
import os
import threading

class DatabaseManager:
    def __init__(self, db_path='distributed_system.db'):
        """Initialize the database manager with the specified database path"""
        self.db_path = db_path
        self.lock = threading.Lock()
        self._create_tables()
    
    def _create_tables(self):
        """Create the necessary tables if they don't exist"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create clients table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                client_type TEXT NOT NULL,
                last_seen REAL NOT NULL,
                is_connected INTEGER DEFAULT 0
            )
            ''')
            
            # Create messages table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                message_type TEXT NOT NULL,
                sender TEXT NOT NULL,
                target TEXT,
                content TEXT NOT NULL,
                timestamp REAL NOT NULL
            )
            ''')
            
            # Create tasks table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id TEXT UNIQUE NOT NULL,
                task_type TEXT NOT NULL,
                worker TEXT NOT NULL,
                requester TEXT NOT NULL,
                parameters TEXT NOT NULL,
                status TEXT NOT NULL,
                submit_time REAL NOT NULL,
                complete_time REAL,
                result TEXT
            )
            ''')
            
            conn.commit()
            conn.close()
    
    def register_client(self, name, client_type):
        """Register a client in the database or update if it already exists"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = time.time()
            
            # Check if client already exists
            cursor.execute("SELECT id FROM clients WHERE name = ?", (name,))
            result = cursor.fetchone()
            
            if result:
                # Update existing client
                cursor.execute(
                    "UPDATE clients SET last_seen = ?, is_connected = 1, client_type = ? WHERE name = ?",
                    (current_time, client_type, name)
                )
            else:
                # Insert new client
                cursor.execute(
                    "INSERT INTO clients (name, client_type, last_seen, is_connected) VALUES (?, ?, ?, 1)",
                    (name, client_type, current_time)
                )
            
            conn.commit()
            conn.close()
    
    def disconnect_client(self, name):
        """Mark a client as disconnected"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE clients SET is_connected = 0 WHERE name = ?",
                (name,)
            )
            
            conn.commit()
            conn.close()
    
    def get_connected_clients(self):
        """Get a list of all connected clients"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT name, client_type FROM clients WHERE is_connected = 1")
            clients = cursor.fetchall()
            
            conn.close()
            
            return [{"name": name, "type": client_type} for name, client_type in clients]
    
    def store_message(self, message_type, sender, content, target=None):
        """Store a message in the database"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = time.time()
            
            cursor.execute(
                "INSERT INTO messages (message_type, sender, target, content, timestamp) VALUES (?, ?, ?, ?, ?)",
                (message_type, sender, target, content, current_time)
            )
            
            conn.commit()
            conn.close()
    
    def get_recent_messages(self, limit=50, target=None):
        """Get recent messages, optionally filtered by target"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if target:
                cursor.execute(
                    "SELECT message_type, sender, target, content, timestamp FROM messages WHERE target IS NULL OR target = ? ORDER BY timestamp DESC LIMIT ?",
                    (target, limit)
                )
            else:
                cursor.execute(
                    "SELECT message_type, sender, target, content, timestamp FROM messages ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
            
            messages = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "type": msg_type,
                    "sender": sender,
                    "target": target,
                    "content": content,
                    "timestamp": timestamp
                }
                for msg_type, sender, target, content, timestamp in messages
            ]
    
    def store_task(self, task_id, task_type, worker, requester, parameters):
        """Store a new task in the database"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = time.time()
            parameters_json = json.dumps(parameters)
            
            cursor.execute(
                """
                INSERT INTO tasks 
                (task_id, task_type, worker, requester, parameters, status, submit_time) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (task_id, task_type, worker, requester, parameters_json, "pending", current_time)
            )
            
            conn.commit()
            conn.close()
    
    def update_task_result(self, task_id, result, status="completed"):
        """Update a task with its result"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            current_time = time.time()
            result_json = json.dumps(result)
            
            cursor.execute(
                """
                UPDATE tasks 
                SET status = ?, complete_time = ?, result = ? 
                WHERE task_id = ?
                """,
                (status, current_time, result_json, task_id)
            )
            
            conn.commit()
            conn.close()
    
    def get_task(self, task_id):
        """Get a specific task by its ID"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
            task = cursor.fetchone()
            
            conn.close()
            
            if task:
                task_dict = dict(task)
                task_dict['parameters'] = json.loads(task_dict['parameters'])
                if task_dict['result']:
                    task_dict['result'] = json.loads(task_dict['result'])
                return task_dict
            return None
    
    def get_tasks_by_requester(self, requester, limit=50):
        """Get tasks submitted by a specific requester"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM tasks WHERE requester = ? ORDER BY submit_time DESC LIMIT ?",
                (requester, limit)
            )
            tasks = cursor.fetchall()
            
            conn.close()
            
            result = []
            for task in tasks:
                task_dict = dict(task)
                task_dict['parameters'] = json.loads(task_dict['parameters'])
                if task_dict['result']:
                    task_dict['result'] = json.loads(task_dict['result'])
                result.append(task_dict)
            
            return result
    
    def get_tasks_by_worker(self, worker, limit=50):
        """Get tasks assigned to a specific worker"""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM tasks WHERE worker = ? ORDER BY submit_time DESC LIMIT ?",
                (worker, limit)
            )
            tasks = cursor.fetchall()
            
            conn.close()
            
            result = []
            for task in tasks:
                task_dict = dict(task)
                task_dict['parameters'] = json.loads(task_dict['parameters'])
                if task_dict['result']:
                    task_dict['result'] = json.loads(task_dict['result'])
                result.append(task_dict)
            
            return result