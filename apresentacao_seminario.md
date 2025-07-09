# Sistema Distribuído em Python


---

##  1: Introdução ao Projeto

### Sistema Distribuído em Python
- **Objetivo**: Demonstrar conceitos fundamentais de sistemas distribuídos
- **Linguagem**: Python 3.x
- **Paradigma**: Arquitetura Cliente-Servidor com comunicação via sockets
- **Características**: Multi-threading, distribuição de tarefas, persistência de dados

---

##  2: Visão Geral da Arquitetura

### Componentes Principais:
1. **Servidor Central** (`server.py`)
   - Coordena toda a comunicação
   - Gerencia conexões de clientes
   - Roteamento de mensagens

2. **Clientes de Comunicação** (`client.py`)
   - Chat distribuído entre usuários
   - Mensagens broadcast e diretas

3. **Workers/Trabalhadores** (`task_worker.py`)
   - Processamento distribuído de tarefas
   - Execução paralela

4. **Clientes de Tarefas** (`task_client.py`)
   - Submissão de tarefas para processamento
   - Monitoramento de resultados

5. **Interface Gráfica** (`gui_app.py`)
   - Interface visual para interação
   - Integração de todas as funcionalidades

6. **Gerenciador de Banco de Dados** (`db_manager.py`)
   - Persistência de dados
   - Histórico de mensagens e tarefas

---

##  3: Tecnologias e Conceitos Utilizados

### Tecnologias Core:
- **Python Sockets (TCP/IP)**: Comunicação confiável entre componentes
- **Threading**: Processamento paralelo e atendimento simultâneo
- **JSON**: Formato de troca de mensagens estruturadas
- **SQLite**: Persistência de dados local
- **Tkinter**: Interface gráfica nativa do Python

### Conceitos de Sistemas Distribuídos:
- **Comunicação entre Processos (IPC)**
- **Balanceamento de Carga**
- **Tolerância a Falhas**
- **Coordenação Distribuída**
- **Paralelismo e Concorrência**

---

##  4: Arquitetura Detalhada do Sistema

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Task Client   │───▶│  Servidor Central │◀───│  Communication  │
│   (Tarefas)     │    │   (Coordenador)   │    │     Client      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   Task Workers   │
                    │  (Processamento) │
                    └──────────────────┘
                               │
                               ▼
                    ┌──────────────────┐
                    │   Database       │
                    │  (Persistência)  │
                    └──────────────────┘
```

### Fluxo de Comunicação:
1. **Registro**: Clientes se registram no servidor
2. **Descoberta**: Servidor mantém lista de clientes ativos
3. **Roteamento**: Mensagens são roteadas entre componentes
4. **Processamento**: Tarefas são distribuídas para workers
5. **Persistência**: Dados são armazenados no banco

---

##  5: Componente Servidor Central

### Funcionalidades Principais:
```python
class DistributedServer:
    def __init__(self, host='localhost', port=5000):
        self.clients = {}           # Conexões ativas
        self.client_names = {}      # Mapeamento nome-endereço
        self.lock = threading.Lock() # Thread safety
        self.db = DatabaseManager() # Persistência
```

### Responsabilidades:
- **Gerenciamento de Conexões**: Aceita e mantém conexões TCP
- **Registro de Clientes**: Identifica tipos de cliente (regular, worker, task_client)
- **Roteamento de Mensagens**: Broadcast, mensagens diretas e distribuição de tarefas
- **Coordenação**: Balanceamento de carga entre workers
- **Persistência**: Armazenamento de mensagens e estado do sistema

---

##  6: Sistema de Comunicação

### Tipos de Mensagem:
1. **Registro**: Identificação do cliente
   ```json
   {"type": "register", "name": "Client-001"}
   ```

2. **Broadcast**: Mensagem para todos
   ```json
   {"type": "broadcast", "message": "Olá a todos!"}
   ```

3. **Mensagem Direta**: Comunicação ponto-a-ponto
   ```json
   {"type": "direct", "target": "Client-002", "message": "Oi!"}
   ```

4. **Tarefa**: Processamento distribuído
   ```json
   {"type": "task", "task_id": "uuid", "operation": "calculate", "data": [1,2,3]}
   ```

### Características:
- **Protocolo JSON**: Estruturação clara de dados
- **Timestamps**: Rastreamento temporal
- **IDs Únicos**: Identificação de tarefas e resultados

---

##  7: Sistema de Processamento Distribuído

### Workers (Trabalhadores):
```python
class DistributedTaskWorker:
    def process_task(self, task_data):
        # Simula processamento de diferentes tipos de tarefa
        if operation == "calculate":
            return sum(data)
        elif operation == "fibonacci":
            return self.fibonacci(data)
```

### Funcionalidades dos Workers:
- **Registro Automático**: Identificação como "Worker-{name}"
- **Processamento de Tarefas**: Cálculos matemáticos, Fibonacci, ordenação
- **Simulação de Carga**: Tempo de processamento variável
- **Relatório de Status**: Confirmação de conclusão

### Task Clients:
- **Submissão de Tarefas**: Criação e envio de tarefas
- **Monitoramento**: Acompanhamento do progresso
- **Coleta de Resultados**: Recebimento de respostas processadas

---

##  8: Persistência e Gerenciamento de Dados

### Banco de Dados SQLite:
```sql
-- Tabela de Clientes
CREATE TABLE clients (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    client_type TEXT NOT NULL,
    last_seen REAL NOT NULL,
    is_connected INTEGER DEFAULT 0
);

-- Tabela de Mensagens
CREATE TABLE messages (
    id INTEGER PRIMARY KEY,
    message_type TEXT NOT NULL,
    sender TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp REAL NOT NULL
);
```

### Funcionalidades do DatabaseManager:
- **Thread Safety**: Operações seguras em ambiente multi-thread
- **Histórico de Mensagens**: Armazenamento persistente
- **Estado dos Clientes**: Rastreamento de conexões
- **Auditoria**: Log completo de atividades do sistema

---

##  9: Interface Gráfica (GUI)

### Tkinter Application:
- **Múltiplas Abas**: Comunicação, Tarefas, Monitoramento
- **Chat em Tempo Real**: Interface de mensagens instantâneas
- **Submissão de Tarefas**: Formulários para criação de tarefas
- **Visualização de Status**: Lista de clientes conectados
- **Logs do Sistema**: Histórico de atividades

### Características da GUI:
```python
class DistributedSystemGUI:
    def __init__(self):
        self.notebook = ttk.Notebook(root)
        # Abas: Chat, Tasks, Monitoring, Logs
```

- **Responsiva**: Atualizações em tempo real
- **Multi-funcional**: Integra todas as funcionalidades
- **User-Friendly**: Interface intuitiva

---

##  10: Processo de Desenvolvimento

### Metodologia de Desenvolvimento:
1. **Análise de Requisitos**
   - Definição dos componentes do sistema
   - Identificação dos padrões de comunicação

2. **Design da Arquitetura**
   - Modelo cliente-servidor
   - Protocolo de comunicação JSON
   - Estrutura de dados

3. **Implementação Incremental**
   - Servidor básico → Clientes → Workers → GUI
   - Testes iterativos de cada componente

4. **Integração e Testes**
   - Testes de comunicação
   - Verificação de concorrência
   - Validação de persistência

### Desafios Encontrados:
- **Concorrência**: Gerenciamento de threads múltiplas
- **Sincronização**: Coordenação entre componentes
- **Tratamento de Erros**: Robustez em falhas de rede
- **Interface**: Integração GUI com sistema distribuído

---

##  11: Funcionalidades Implementadas

### Sistema de Comunicação:
✅ **Chat Distribuído**: Mensagens broadcast e diretas  
✅ **Registro de Clientes**: Identificação automática  
✅ **Lista de Usuários**: Descoberta dinâmica de participantes  

### Processamento Distribuído:
✅ **Distribuição de Tarefas**: Envio automático para workers disponíveis  
✅ **Balanceamento de Carga**: Distribuição equitativa  
✅ **Processamento Paralelo**: Múltiplas tarefas simultâneas  
✅ **Coleta de Resultados**: Consolidação de respostas  

### Persistência:
✅ **Histórico de Mensagens**: Armazenamento permanente  
✅ **Estado do Sistema**: Rastreamento de clientes  
✅ **Logs de Atividade**: Auditoria completa  

### Interface:
✅ **GUI Integrada**: Interface visual completa  
✅ **Monitoramento em Tempo Real**: Status dos componentes  

---

##  12: Como Executar o Sistema

### Pré-requisitos:
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente (Windows)
venv\Scripts\activate

# Instalar dependências (se necessário)
pip install -r requirements.txt
```

### Execução:
1. **Iniciar o Servidor**:
   ```bash
   python server.py
   ```

2. **Executar Clientes** (em terminais separados):
   ```bash
   # Cliente de comunicação
   python client.py

   # Worker para processamento
   python task_worker.py

   # Cliente de tarefas
   python task_client.py

   # Interface gráfica
   python gui_app.py
   ```

---

##  13: Demonstração Prática

### Cenário de Demonstração:
1. **Inicialização**: Servidor + múltiplos workers + task client
2. **Comunicação**: Troca de mensagens entre clientes
3. **Processamento**: Submissão e execução de tarefas
4. **Monitoramento**: Visualização em tempo real via GUI
5. **Persistência**: Verificação do banco de dados

### Métricas a Observar:
- **Latência**: Tempo de resposta das mensagens
- **Throughput**: Capacidade de processamento
- **Escalabilidade**: Adição dinâmica de workers
- **Confiabilidade**: Tratamento de desconexões

---

##  14: Conceitos de Sistemas Distribuídos Demonstrados

### Implementados no Projeto:
- **Comunicação Assíncrona**: Threading para não-bloqueio
- **Distribuição de Carga**: Workers processam em paralelo
- **Descoberta de Serviços**: Registro automático de componentes
- **Coordenação Centralizada**: Servidor como coordenador
- **Persistência Distribuída**: Estado compartilhado via banco
- **Tolerância a Falhas**: Reconexão automática (parcial)

### Conceitos para Expansão Futura:
- **Consenso Distribuído**: Algoritmos como Raft ou PBFT
- **Replicação**: Múltiplos servidores para alta disponibilidade
- **Particionamento**: Sharding de dados
- **Descoberta P2P**: Eliminação do ponto único de falha

---

##  15: Resultados e Aprendizados

### Resultados Alcançados:
✅ **Sistema Funcional**: Comunicação e processamento distribuído  
✅ **Arquitetura Escalável**: Fácil adição de novos componentes  
✅ **Interface Completa**: GUI integrando todas as funcionalidades  
✅ **Persistência Robusta**: Dados mantidos entre execuções  

### Aprendizados Principais:
- **Complexidade da Coordenação**: Sincronização entre componentes
- **Importância do Design**: Arquitetura bem definida facilita implementação
- **Tratamento de Concorrência**: Threading requer cuidado especial
- **Debugging Distribuído**: Desafios únicos em sistemas distribuídos

### Métricas de Sucesso:
- **Múltiplos clientes simultâneos**: ✅ Testado com 5+ clientes
- **Processamento paralelo**: ✅ Múltiplas tarefas simultâneas
- **Persistência**: ✅ Dados mantidos entre reinicializações
- **Interface responsiva**: ✅ GUI atualiza em tempo real

---

##  16: Conclusões e Trabalhos Futuros

### Conclusões:
- **Viabilidade**: Python é adequado para prototipação de sistemas distribuídos
- **Escalabilidade**: Arquitetura permite expansão com modificações mínimas
- **Aprendizado**: Projeto demonstra conceitos fundamentais efetivamente
- **Aplicabilidade**: Base sólida para sistemas mais complexos

### Trabalhos Futuros:
1. **Alta Disponibilidade**: Implementar replicação do servidor
2. **Algoritmos de Consenso**: Adicionar Raft ou similar
3. **Descoberta P2P**: Eliminar dependência do servidor central
4. **Segurança**: Autenticação e criptografia
5. **Monitoramento**: Métricas avançadas de performance
6. **Load Balancing**: Algoritmos mais sofisticados
7. **Containerização**: Deploy com Docker/Kubernetes

---

##  17: Perguntas e Discussão

### Tópicos para Discussão:
- **Escalabilidade**: Como o sistema se comportaria com 100+ clientes?
- **Falhas**: Que tipos de falhas o sistema pode tolerar?
- **Performance**: Gargalos identificados e otimizações possíveis
- **Aplicações Reais**: Onde este design seria aplicável?
- **Comparações**: Como se compara a frameworks como Apache Kafka, Redis?

### Demonstração Interativa:
- **Execução ao vivo** do sistema
- **Adição/remoção** dinâmica de componentes
- **Visualização** do banco de dados
- **Análise** dos logs de comunicação

---

##  18: Referências e Recursos

### Documentação Técnica:
- **Python Socket Programming**: Comunicação TCP/IP
- **Threading in Python**: Concorrência e paralelismo
- **SQLite Documentation**: Persistência local
- **Tkinter Guide**: Interface gráfica nativa

### Conceitos de Sistemas Distribuídos:
- **"Distributed Systems" - Tanenbaum & Van Steen**
- **"Designing Data-Intensive Applications" - Martin Kleppmann**
- **Papers sobre Consensus Algorithms (Raft, PBFT)**

### Código Fonte:
- **GitHub Repository**: [link do repositório]
- **Documentação Completa**: README.md
- **Exemplos de Uso**: Scripts de demonstração

---

## Obrigado!
### Perguntas?

**Contato**: [seu_email@exemplo.com]  
**Repositório**: [link_do_github]  
**Documentação**: README.md no projeto
