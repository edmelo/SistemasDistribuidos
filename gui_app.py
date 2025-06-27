import os
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import json
import time
import uuid
import socket
import random

# Fix for Tcl/Tk initialization error
def setup_tcl_tk_env():
    """Set up Tcl/Tk environment variables to help Python find the Tcl/Tk files"""
    python_dir = os.path.dirname(sys.executable)

    # Try to find tcl directory
    tcl_dirs = []

    # Check standard locations relative to Python installation
    tcl_dirs.append(os.path.join(python_dir, 'tcl'))
    tcl_dirs.append(os.path.join(python_dir, 'lib', 'tcl8.6'))
    tcl_dirs.append(os.path.join(python_dir, 'lib', 'tcl'))

    # Check for Tcl in the Python installation directory
    for root, dirs, files in os.walk(python_dir):
        for dir_name in dirs:
            if dir_name.startswith('tcl'):
                tcl_dirs.append(os.path.join(root, dir_name))

    # Check if any of these directories exist and contain init.tcl
    for tcl_dir in tcl_dirs:
        if os.path.exists(tcl_dir):
            # Look for init.tcl in the library subdirectory
            library_dir = os.path.join(tcl_dir, 'library')
            if os.path.exists(os.path.join(library_dir, 'init.tcl')):
                os.environ['TCL_LIBRARY'] = library_dir
                print(f"Set TCL_LIBRARY to {library_dir}")
                break

            # Or directly in the tcl directory
            if os.path.exists(os.path.join(tcl_dir, 'init.tcl')):
                os.environ['TCL_LIBRARY'] = tcl_dir
                print(f"Set TCL_LIBRARY to {tcl_dir}")
                break

    # Try to find tk directory similarly
    tk_dirs = []
    tk_dirs.append(os.path.join(python_dir, 'tk'))
    tk_dirs.append(os.path.join(python_dir, 'lib', 'tk8.6'))
    tk_dirs.append(os.path.join(python_dir, 'lib', 'tk'))

    for root, dirs, files in os.walk(python_dir):
        for dir_name in dirs:
            if dir_name.startswith('tk'):
                tk_dirs.append(os.path.join(root, dir_name))

    for tk_dir in tk_dirs:
        if os.path.exists(tk_dir):
            library_dir = os.path.join(tk_dir, 'library')
            if os.path.exists(os.path.join(library_dir, 'tk.tcl')):
                os.environ['TK_LIBRARY'] = library_dir
                print(f"Set TK_LIBRARY to {library_dir}")
                break

            if os.path.exists(os.path.join(tk_dir, 'tk.tcl')):
                os.environ['TK_LIBRARY'] = tk_dir
                print(f"Set TK_LIBRARY to {tk_dir}")
                break

class DistributedSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Distribuído")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        # Set up the main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create a notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.welcome_tab = ttk.Frame(self.notebook)
        self.client_tab = ttk.Frame(self.notebook)
        self.task_client_tab = ttk.Frame(self.notebook)
        self.worker_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.welcome_tab, text="Bem-vindo")
        self.notebook.add(self.client_tab, text="Cliente de Comunicação")
        self.notebook.add(self.task_client_tab, text="Cliente de Tarefas")
        self.notebook.add(self.worker_tab, text="Trabalhador")

        # Set up the welcome tab
        self.setup_welcome_tab()

        # Set up the client tabs
        self.setup_client_tab()
        self.setup_task_client_tab()
        self.setup_worker_tab()

        # Initialize client objects
        self.comm_client = None
        self.task_client = None
        self.worker = None

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Desconectado")
        self.status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_welcome_tab(self):
        """Set up the welcome tab with connection options"""
        welcome_frame = ttk.Frame(self.welcome_tab, padding="20")
        welcome_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_label = ttk.Label(welcome_frame, text="Sistema Distribuído em Python", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)

        # Description
        desc_text = (
            "Este sistema demonstra conceitos de sistemas distribuídos como comunicação entre processos, "
            "arquitetura cliente-servidor, processamento paralelo e distribuição de tarefas."
        )
        desc_label = ttk.Label(welcome_frame, text=desc_text, wraplength=600, justify=tk.CENTER)
        desc_label.pack(pady=10)

        # Connection frame
        conn_frame = ttk.LabelFrame(welcome_frame, text="Conexão ao Servidor", padding="10")
        conn_frame.pack(pady=20, fill=tk.X)

        # Server settings
        settings_frame = ttk.Frame(conn_frame)
        settings_frame.pack(fill=tk.X, pady=10)

        ttk.Label(settings_frame, text="Host:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.host_var = tk.StringVar(value="localhost")
        ttk.Entry(settings_frame, textvariable=self.host_var, width=20).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        ttk.Label(settings_frame, text="Porta:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.port_var = tk.StringVar(value="5000")
        ttk.Entry(settings_frame, textvariable=self.port_var, width=10).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)

        ttk.Label(settings_frame, text="Nome:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_var = tk.StringVar(value="User-" + str(random.randint(1000, 9999)))
        ttk.Entry(settings_frame, textvariable=self.name_var, width=20).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        # Connect buttons
        buttons_frame = ttk.Frame(conn_frame)
        buttons_frame.pack(fill=tk.X, pady=10)

        ttk.Button(buttons_frame, text="Conectar como Cliente", command=self.connect_as_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Conectar como Cliente de Tarefas", command=self.connect_as_task_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Conectar como Trabalhador", command=self.connect_as_worker).pack(side=tk.LEFT, padx=5)

    def setup_client_tab(self):
        """Set up the communication client tab"""
        client_frame = ttk.Frame(self.client_tab, padding="10")
        client_frame.pack(fill=tk.BOTH, expand=True)

        # Split the frame into two parts
        left_frame = ttk.Frame(client_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(client_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        # Messages area
        messages_frame = ttk.LabelFrame(left_frame, text="Mensagens", padding="5")
        messages_frame.pack(fill=tk.BOTH, expand=True)

        self.client_messages = scrolledtext.ScrolledText(messages_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.client_messages.pack(fill=tk.BOTH, expand=True, pady=5)

        # Input area
        input_frame = ttk.Frame(left_frame)
        input_frame.pack(fill=tk.X, pady=(10, 0))

        self.client_input = ttk.Entry(input_frame)
        self.client_input.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.client_input.bind("<Return>", self.send_client_message)

        ttk.Button(input_frame, text="Enviar", command=self.send_client_message).pack(side=tk.RIGHT, padx=(5, 0))

        # Clients list
        clients_frame = ttk.LabelFrame(right_frame, text="Clientes Conectados", padding="5")
        clients_frame.pack(fill=tk.BOTH, expand=True)

        self.clients_listbox = tk.Listbox(clients_frame, width=25)
        self.clients_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        # Direct message
        dm_frame = ttk.LabelFrame(right_frame, text="Mensagem Direta", padding="5")
        dm_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(dm_frame, text="Para:").pack(anchor=tk.W)
        self.dm_target = ttk.Entry(dm_frame)
        self.dm_target.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(dm_frame, text="Mensagem:").pack(anchor=tk.W)
        self.dm_message = ttk.Entry(dm_frame)
        self.dm_message.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(dm_frame, text="Enviar", command=self.send_direct_message).pack(anchor=tk.E)

        # Buttons
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(buttons_frame, text="Atualizar Lista", command=self.request_client_list).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="Desconectar", command=self.disconnect_client).pack(fill=tk.X, pady=2)

    def setup_task_client_tab(self):
        """Set up the task client tab"""
        task_frame = ttk.Frame(self.task_client_tab, padding="10")
        task_frame.pack(fill=tk.BOTH, expand=True)

        # Split the frame into two parts
        left_frame = ttk.Frame(task_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = ttk.Frame(task_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))

        # Task submission area
        task_submit_frame = ttk.LabelFrame(left_frame, text="Submeter Tarefa", padding="5")
        task_submit_frame.pack(fill=tk.X, pady=(0, 10))

        # Worker selection
        worker_frame = ttk.Frame(task_submit_frame)
        worker_frame.pack(fill=tk.X, pady=5)

        ttk.Label(worker_frame, text="Trabalhador:").pack(side=tk.LEFT)
        self.worker_var = tk.StringVar()
        self.worker_dropdown = ttk.Combobox(worker_frame, textvariable=self.worker_var, state="readonly")
        self.worker_dropdown.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        # Task type selection
        task_type_frame = ttk.Frame(task_submit_frame)
        task_type_frame.pack(fill=tk.X, pady=5)

        ttk.Label(task_type_frame, text="Tipo de Tarefa:").pack(side=tk.LEFT)
        self.task_type_var = tk.StringVar(value="calculate")
        ttk.Radiobutton(task_type_frame, text="Cálculo", variable=self.task_type_var, value="calculate").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Radiobutton(task_type_frame, text="Texto", variable=self.task_type_var, value="process_text").pack(side=tk.LEFT, padx=(5, 0))

        # Operation selection
        op_frame = ttk.Frame(task_submit_frame)
        op_frame.pack(fill=tk.X, pady=5)

        ttk.Label(op_frame, text="Operação:").pack(side=tk.LEFT)
        self.operation_var = tk.StringVar()
        self.operation_dropdown = ttk.Combobox(op_frame, textvariable=self.operation_var, state="readonly")
        self.operation_dropdown.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        # Set up operation options based on task type
        self.task_type_var.trace_add("write", self.update_operation_options)
        self.update_operation_options()

        # Parameters
        params_frame = ttk.Frame(task_submit_frame)
        params_frame.pack(fill=tk.X, pady=5)

        ttk.Label(params_frame, text="Parâmetros:").pack(side=tk.LEFT)
        self.params_entry = ttk.Entry(params_frame)
        self.params_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)

        # Submit button
        ttk.Button(task_submit_frame, text="Submeter Tarefa", command=self.submit_task).pack(anchor=tk.E, pady=(5, 0))

        # Results area
        results_frame = ttk.LabelFrame(left_frame, text="Resultados", padding="5")
        results_frame.pack(fill=tk.BOTH, expand=True)

        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.results_text.pack(fill=tk.BOTH, expand=True, pady=5)

        # Workers list
        workers_frame = ttk.LabelFrame(right_frame, text="Trabalhadores Disponíveis", padding="5")
        workers_frame.pack(fill=tk.BOTH, expand=True)

        self.workers_listbox = tk.Listbox(workers_frame, width=25)
        self.workers_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.workers_listbox.bind("<<ListboxSelect>>", self.on_worker_select)

        # Buttons
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(buttons_frame, text="Atualizar Lista", command=self.request_worker_list).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="Limpar Resultados", command=self.clear_results).pack(fill=tk.X, pady=2)
        ttk.Button(buttons_frame, text="Desconectar", command=self.disconnect_task_client).pack(fill=tk.X, pady=2)

    def setup_worker_tab(self):
        """Set up the worker tab"""
        worker_frame = ttk.Frame(self.worker_tab, padding="10")
        worker_frame.pack(fill=tk.BOTH, expand=True)

        # Status area
        status_frame = ttk.LabelFrame(worker_frame, text="Status do Trabalhador", padding="5")
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.worker_status_var = tk.StringVar(value="Desconectado")
        ttk.Label(status_frame, textvariable=self.worker_status_var, font=("Arial", 12)).pack(pady=5)

        # Task log area
        log_frame = ttk.LabelFrame(worker_frame, text="Registro de Tarefas", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.worker_log = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state=tk.DISABLED)
        self.worker_log.pack(fill=tk.BOTH, expand=True, pady=5)

        # Buttons
        buttons_frame = ttk.Frame(worker_frame)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(buttons_frame, text="Limpar Registro", command=self.clear_worker_log).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Desconectar", command=self.disconnect_worker).pack(side=tk.LEFT, padx=5)

    def update_operation_options(self, *args):
        """Update operation options based on task type"""
        task_type = self.task_type_var.get()

        if task_type == "calculate":
            operations = ["sum", "average", "max", "min"]
        else:  # process_text
            operations = ["count_words", "count_chars", "uppercase", "lowercase"]

        self.operation_dropdown['values'] = operations
        if operations:
            self.operation_dropdown.current(0)

    def connect_as_client(self):
        """Connect as a communication client"""
        try:
            host = self.host_var.get()
            port = int(self.port_var.get())
            name = self.name_var.get()

            # Create client
            from client import DistributedClient
            self.comm_client = DistributedClient(name, host, port)

            if self.comm_client.connect():
                self.status_var.set(f"Conectado como Cliente: {name}")
                self.notebook.select(self.client_tab)

                # Start a thread to receive messages
                threading.Thread(target=self.process_client_messages, daemon=True).start()

                # Request client list
                self.request_client_list()
            else:
                messagebox.showerror("Erro de Conexão", "Não foi possível conectar ao servidor.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar: {str(e)}")

    def connect_as_task_client(self):
        """Connect as a task client"""
        try:
            host = self.host_var.get()
            port = int(self.port_var.get())
            name = self.name_var.get()

            # Create task client
            from task_client import DistributedTaskClient
            self.task_client = DistributedTaskClient(name, host, port)

            if self.task_client.connect():
                self.status_var.set(f"Conectado como Cliente de Tarefas: {name}")
                self.notebook.select(self.task_client_tab)

                # Start a thread to receive messages
                threading.Thread(target=self.process_task_client_messages, daemon=True).start()

                # Request client list
                self.request_worker_list()
            else:
                messagebox.showerror("Erro de Conexão", "Não foi possível conectar ao servidor.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar: {str(e)}")

    def connect_as_worker(self):
        """Connect as a worker"""
        try:
            host = self.host_var.get()
            port = int(self.port_var.get())
            name = self.name_var.get()

            # Create worker
            from task_worker import DistributedTaskWorker
            self.worker = DistributedTaskWorker(name, host, port)

            if self.worker.connect():
                self.status_var.set(f"Conectado como Trabalhador: Worker-{name}")
                self.notebook.select(self.worker_tab)
                self.worker_status_var.set(f"Trabalhador Worker-{name} conectado e pronto para processar tarefas")

                # Start a thread to receive messages
                threading.Thread(target=self.process_worker_messages, daemon=True).start()

                # Broadcast status
                self.worker.broadcast_status("ready for tasks")
                self.add_to_worker_log("Trabalhador iniciado e pronto para processar tarefas")
            else:
                messagebox.showerror("Erro de Conexão", "Não foi possível conectar ao servidor.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar: {str(e)}")

    def process_client_messages(self):
        """Process messages for the communication client"""
        if not self.comm_client:
            return

        while self.comm_client.connected:
            time.sleep(0.1)  # Small delay to prevent high CPU usage

            # Process any new messages
            if hasattr(self.comm_client, 'new_messages'):
                while self.comm_client.new_messages:
                    message = self.comm_client.new_messages.pop(0)
                    self.handle_client_message(message)

    def process_task_client_messages(self):
        """Process messages for the task client"""
        if not self.task_client:
            return

        while self.task_client.connected:
            time.sleep(0.1)  # Small delay to prevent high CPU usage

            # Process any new messages or task results
            if hasattr(self.task_client, 'new_messages'):
                while self.task_client.new_messages:
                    message = self.task_client.new_messages.pop(0)
                    self.handle_task_client_message(message)

            # Update worker list if needed
            if hasattr(self.task_client, 'client_list_updated') and self.task_client.client_list_updated:
                self.task_client.client_list_updated = False
                self.update_worker_dropdown()

    def process_worker_messages(self):
        """Process messages for the worker"""
        if not self.worker:
            return

        while self.worker.connected:
            time.sleep(0.1)  # Small delay to prevent high CPU usage

            # Process any new messages or tasks
            if hasattr(self.worker, 'new_messages'):
                while self.worker.new_messages:
                    message = self.worker.new_messages.pop(0)
                    self.handle_worker_message(message)

            # Update worker status
            if hasattr(self.worker, 'processing') and self.worker.processing:
                self.worker_status_var.set("Processando tarefa...")
            else:
                self.worker_status_var.set(f"Trabalhador Worker-{self.worker.name} pronto para processar tarefas")

    def handle_client_message(self, message):
        """Handle a message received by the communication client"""
        message_type = message.get('type')

        if message_type == 'broadcast':
            sender = message.get('sender', 'Unknown')
            msg_text = message.get('message', '')
            self.add_to_client_messages(f"[Broadcast] {sender}: {msg_text}")

        elif message_type == 'direct':
            sender = message.get('sender', 'Unknown')
            msg_text = message.get('message', '')
            self.add_to_client_messages(f"[Direct from {sender}] {msg_text}")

        elif message_type == 'system':
            msg_text = message.get('message', '')
            self.add_to_client_messages(f"[System] {msg_text}")

        elif message_type == 'client_list':
            self.update_clients_listbox(message.get('clients', []))

    def handle_task_client_message(self, message):
        """Handle a message received by the task client"""
        message_type = message.get('type')

        if message_type == 'direct':
            sender = message.get('sender', 'Unknown')
            msg_text = message.get('message', '')

            # Check if this is a task result
            task_result = message.get('task_result')
            if task_result:
                task_id = task_result.get('task_id')
                result = task_result.get('result')
                processing_time = task_result.get('processing_time', 0)

                result_text = f"Task {task_id} completed by {sender} in {processing_time:.2f}s\nResult: {result}"
                self.add_to_results(result_text)
            else:
                self.add_to_results(f"[Direct from {sender}] {msg_text}")

        elif message_type == 'system':
            msg_text = message.get('message', '')
            self.add_to_results(f"[System] {msg_text}")

        elif message_type == 'client_list':
            clients = message.get('clients', [])
            # Filter for workers only
            workers = [c for c in clients if c.startswith("Worker-")]
            self.update_workers_listbox(workers)

    def handle_worker_message(self, message):
        """Handle a message received by the worker"""
        message_type = message.get('type')

        if message_type == 'direct':
            sender = message.get('sender', 'Unknown')
            msg_text = message.get('message', '')

            # Check if this is a task request
            task_data = message.get('task_data')
            task_id = message.get('task_id')

            if task_data and task_id:
                task_type = task_data.get('task_type', 'unknown')
                params = task_data.get('params', {})

                task_info = f"Received task {task_id} from {sender}:\nType: {task_type}\nParams: {params}"
                self.add_to_worker_log(task_info)
            else:
                self.add_to_worker_log(f"[Direct from {sender}] {msg_text}")

        elif message_type == 'system':
            msg_text = message.get('message', '')
            self.add_to_worker_log(f"[System] {msg_text}")

    def add_to_client_messages(self, text):
        """Add text to the client messages area"""
        self.client_messages.config(state=tk.NORMAL)
        self.client_messages.insert(tk.END, text + "\n")
        self.client_messages.see(tk.END)
        self.client_messages.config(state=tk.DISABLED)

    def add_to_results(self, text):
        """Add text to the results area"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.insert(tk.END, text + "\n\n")
        self.results_text.see(tk.END)
        self.results_text.config(state=tk.DISABLED)

    def add_to_worker_log(self, text):
        """Add text to the worker log area"""
        self.worker_log.config(state=tk.NORMAL)
        self.worker_log.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {text}\n\n")
        self.worker_log.see(tk.END)
        self.worker_log.config(state=tk.DISABLED)

    def update_clients_listbox(self, clients):
        """Update the clients listbox"""
        self.clients_listbox.delete(0, tk.END)
        for client in clients:
            self.clients_listbox.insert(tk.END, client)

    def update_workers_listbox(self, workers):
        """Update the workers listbox"""
        self.workers_listbox.delete(0, tk.END)
        for worker in workers:
            self.workers_listbox.insert(tk.END, worker)

        # Also update the dropdown
        self.update_worker_dropdown()

    def update_worker_dropdown(self):
        """Update the worker dropdown in the task client tab"""
        if not self.task_client:
            return

        workers = [c for c in self.task_client.client_list if c.startswith("Worker-")]
        self.worker_dropdown['values'] = workers
        if workers and not self.worker_var.get():
            self.worker_var.set(workers[0])

    def on_worker_select(self, event):
        """Handle worker selection from the listbox"""
        selection = self.workers_listbox.curselection()
        if selection:
            worker = self.workers_listbox.get(selection[0])
            self.worker_var.set(worker)

    def send_client_message(self, event=None):
        """Send a message from the communication client"""
        if not self.comm_client or not self.comm_client.connected:
            messagebox.showerror("Erro", "Cliente não conectado")
            return

        message = self.client_input.get()
        if not message:
            return

        if message.startswith('/'):
            # Handle commands
            if message.lower() == '/list':
                self.request_client_list()
            elif message.lower().startswith('/msg '):
                parts = message[5:].strip().split(' ', 1)
                if len(parts) == 2:
                    target, msg = parts
                    self.comm_client.send_direct_message(target, msg)
                    self.add_to_client_messages(f"[Direct to {target}] {msg}")
                else:
                    self.add_to_client_messages("Usage: /msg <client> <message>")
            else:
                self.add_to_client_messages(f"Unknown command: {message}")
        else:
            # Broadcast message
            self.comm_client.broadcast_message(message)
            self.add_to_client_messages(f"[You] {message}")

        # Clear input
        self.client_input.delete(0, tk.END)

    def send_direct_message(self):
        """Send a direct message from the communication client"""
        if not self.comm_client or not self.comm_client.connected:
            messagebox.showerror("Erro", "Cliente não conectado")
            return

        target = self.dm_target.get()
        message = self.dm_message.get()

        if not target or not message:
            messagebox.showerror("Erro", "Destinatário e mensagem são obrigatórios")
            return

        self.comm_client.send_direct_message(target, message)
        self.add_to_client_messages(f"[Direct to {target}] {message}")

        # Clear inputs
        self.dm_target.delete(0, tk.END)
        self.dm_message.delete(0, tk.END)

    def submit_task(self):
        """Submit a task from the task client"""
        if not self.task_client or not self.task_client.connected:
            messagebox.showerror("Erro", "Cliente de tarefas não conectado")
            return

        worker = self.worker_var.get()
        task_type = self.task_type_var.get()
        operation = self.operation_var.get()
        params_text = self.params_entry.get()

        if not worker or not operation or not params_text:
            messagebox.showerror("Erro", "Todos os campos são obrigatórios")
            return

        try:
            if task_type == "calculate":
                # Parse numbers for calculation tasks
                numbers = [float(n) for n in params_text.split()]
                params = {
                    'operation': operation,
                    'numbers': numbers
                }
            else:  # process_text
                params = {
                    'operation': operation,
                    'text': params_text
                }

            # Submit the task
            task_id = self.task_client.submit_task(worker, task_type, params)

            if task_id:
                self.add_to_results(f"Task {task_id} submitted to {worker}\nType: {task_type}\nOperation: {operation}\nParams: {params_text}")
                # Clear params
                self.params_entry.delete(0, tk.END)
            else:
                messagebox.showerror("Erro", "Falha ao submeter tarefa")

        except ValueError:
            messagebox.showerror("Erro", "Formato de parâmetros inválido")

    def request_client_list(self):
        """Request the client list from the server"""
        if self.comm_client and self.comm_client.connected:
            self.comm_client.request_client_list()

    def request_worker_list(self):
        """Request the client list to find workers"""
        if self.task_client and self.task_client.connected:
            self.task_client.request_client_list()

    def clear_results(self):
        """Clear the results area"""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state=tk.DISABLED)

    def clear_worker_log(self):
        """Clear the worker log area"""
        self.worker_log.config(state=tk.NORMAL)
        self.worker_log.delete(1.0, tk.END)
        self.worker_log.config(state=tk.DISABLED)

    def disconnect_client(self):
        """Disconnect the communication client"""
        if self.comm_client:
            self.comm_client.disconnect()
            self.comm_client = None
            self.status_var.set("Desconectado")
            self.notebook.select(self.welcome_tab)

    def disconnect_task_client(self):
        """Disconnect the task client"""
        if self.task_client:
            self.task_client.disconnect()
            self.task_client = None
            self.status_var.set("Desconectado")
            self.notebook.select(self.welcome_tab)

    def disconnect_worker(self):
        """Disconnect the worker"""
        if self.worker:
            self.worker.disconnect()
            self.worker = None
            self.status_var.set("Desconectado")
            self.worker_status_var.set("Desconectado")
            self.notebook.select(self.welcome_tab)

    def on_closing(self):
        """Handle window closing"""
        # Disconnect all clients
        if self.comm_client:
            self.comm_client.disconnect()
        if self.task_client:
            self.task_client.disconnect()
        if self.worker:
            self.worker.disconnect()

        self.root.destroy()

# Monkey patch the client classes to store messages for the GUI
def patch_client_class():
    from client import DistributedClient

    original_process_message = DistributedClient.process_message

    def patched_process_message(self, message):
        # Call the original method
        original_process_message(self, message)

        # Store the message for the GUI
        if not hasattr(self, 'new_messages'):
            self.new_messages = []
        self.new_messages.append(message)

    DistributedClient.process_message = patched_process_message

def patch_task_client_class():
    from task_client import DistributedTaskClient

    original_process_message = DistributedTaskClient.process_message

    def patched_process_message(self, message):
        # Call the original method
        original_process_message(self, message)

        # Store the message for the GUI
        if not hasattr(self, 'new_messages'):
            self.new_messages = []
        self.new_messages.append(message)

        # Flag for client list updates
        if message.get('type') == 'client_list':
            self.client_list_updated = True

    DistributedTaskClient.process_message = patched_process_message

def patch_worker_class():
    from task_worker import DistributedTaskWorker

    original_process_message = DistributedTaskWorker.process_message

    def patched_process_message(self, message):
        # Call the original method
        original_process_message(self, message)

        # Store the message for the GUI
        if not hasattr(self, 'new_messages'):
            self.new_messages = []
        self.new_messages.append(message)

    DistributedTaskWorker.process_message = patched_process_message

if __name__ == "__main__":
    # Apply monkey patches
    patch_client_class()
    patch_task_client_class()
    patch_worker_class()

    # Set up Tcl/Tk environment variables to fix initialization error
    setup_tcl_tk_env()

    # Create and run the GUI
    root = tk.Tk()
    app = DistributedSystemGUI(root)
    root.mainloop()
