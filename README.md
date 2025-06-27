# Sistema Distribuído em Python

### Configuração do Ambiente

É recomendado o uso de um ambiente virtual para isolar as dependências do projeto.

1.  **Crie o ambiente virtual:**
    ```
    python -m venv venv
    ```

2.  **Ative o ambiente virtual:**
    ```
    venv\Scripts\activate
    ```

Este projeto implementa um sistema distribuído simples usando Python, demonstrando conceitos fundamentais de sistemas distribuídos como comunicação entre processos, arquitetura cliente-servidor, processamento paralelo e distribuição de tarefas.

## Arquitetura do Sistema

O sistema é composto por quatro componentes principais:

1. **Servidor Central**: Gerencia conexões, roteia mensagens e coordena a comunicação entre os clientes.
2. **Clientes de Comunicação**: Permitem que usuários se conectem ao sistema e troquem mensagens.
3. **Trabalhadores (Workers)**: Nós de processamento que executam tarefas distribuídas.
4. **Clientes de Tarefas**: Submetem tarefas para serem processadas pelos trabalhadores.

### Características da Arquitetura

- **Arquitetura Cliente-Servidor**: O servidor central coordena todas as comunicações.
- **Comunicação via Sockets TCP/IP**: Garante comunicação confiável entre os componentes.
- **Formato de Mensagens JSON**: Facilita a troca de dados estruturados.
- **Multi-threading**: Permite o processamento paralelo e atendimento simultâneo de múltiplos clientes.
- **Balanceamento de Carga**: Distribui tarefas entre os trabalhadores disponíveis.

## Componentes do Sistema

### Servidor (`server.py`)

O servidor é o componente central do sistema, responsável por:
- Aceitar conexões de clientes
- Gerenciar a lista de clientes conectados
- Rotear mensagens entre clientes
- Facilitar a comunicação entre clientes de tarefas e trabalhadores

### Cliente de Comunicação (`client.py`)

O cliente de comunicação permite que usuários:
- Conectem-se ao servidor
- Enviem mensagens para todos os clientes (broadcast)
- Enviem mensagens diretas para clientes específicos
- Visualizem a lista de clientes conectados

### Trabalhador (`task_worker.py`)

O trabalhador é um nó de processamento que:
- Conecta-se ao servidor como um cliente especializado
- Recebe solicitações de tarefas
- Processa tarefas em threads separadas
- Retorna resultados aos solicitantes

Tipos de tarefas suportadas:
- **Cálculos**: soma, média, máximo, mínimo
- **Processamento de texto**: contagem de palavras, contagem de caracteres, conversão para maiúsculas/minúsculas

### Cliente de Tarefas (`task_client.py`)

O cliente de tarefas permite que usuários:
- Conectem-se ao servidor
- Visualizem trabalhadores disponíveis
- Submetam tarefas para processamento
- Recebam e visualizem resultados das tarefas

## Conceitos de Sistemas Distribuídos Demonstrados

1. **Comunicação entre Processos**: O sistema utiliza sockets TCP/IP para comunicação entre diferentes processos, que podem estar em máquinas diferentes.

2. **Arquitetura Cliente-Servidor**: A arquitetura central do sistema segue o modelo cliente-servidor, onde o servidor coordena todas as comunicações.

3. **Processamento Paralelo**: Múltiplas tarefas podem ser processadas simultaneamente por diferentes trabalhadores.

4. **Distribuição de Tarefas**: As tarefas são distribuídas entre os trabalhadores disponíveis, demonstrando balanceamento de carga.

5. **Transparência de Localização**: Os clientes não precisam conhecer a localização física dos trabalhadores para submeter tarefas.

6. **Escalabilidade**: O sistema pode escalar horizontalmente adicionando mais trabalhadores para aumentar a capacidade de processamento.

7. **Tolerância a Falhas**: O sistema lida com desconexões de clientes e trabalhadores de forma graciosa.

8. **Sincronização**: O uso de threads e locks garante operações thread-safe e evita condições de corrida.

## Como Executar o Sistema

### Requisitos

- Python 3.6 ou superior
- Bibliotecas padrão do Python (não requer instalação de pacotes adicionais)

### Passos para Execução

1. **Iniciar o Servidor**:
   ```
   python server.py
   ```

2. **Iniciar um ou mais Clientes de Comunicação**:
   ```
   python client.py [nome_do_cliente]
   ```
   Se o nome não for fornecido, será solicitado durante a execução.

3. **Iniciar um ou mais Trabalhadores**:
   ```
   python task_worker.py [nome_do_trabalhador]
   ```
   Se o nome não for fornecido, será gerado automaticamente.

4. **Iniciar um ou mais Clientes de Tarefas**:
   ```
   python task_client.py [nome_do_cliente]
   ```
   Se o nome não for fornecido, será solicitado durante a execução.

### Comandos do Cliente de Comunicação

- `/list` - Mostrar clientes conectados
- `/msg <cliente> <mensagem>` - Enviar mensagem direta para um cliente
- `/quit` - Desconectar e sair
- Qualquer outro texto será transmitido para todos os clientes

### Comandos do Cliente de Tarefas

- `/list` - Mostrar clientes conectados
- `/workers` - Mostrar trabalhadores disponíveis
- `/calculate <trabalhador> <operação> <números>` - Submeter tarefa de cálculo
  - Operações: sum, average, max, min
  - Exemplo: `/calculate Worker-1234 sum 10 20 30 40`
- `/text <trabalhador> <operação> <texto>` - Submeter tarefa de processamento de texto
  - Operações: count_words, count_chars, uppercase, lowercase
  - Exemplo: `/text Worker-1234 count_words Este é um exemplo de texto`
- `/results` - Mostrar resultados das tarefas
- `/quit` - Desconectar e sair

## Exemplo de Uso

1. Inicie o servidor
2. Inicie pelo menos um trabalhador
3. Inicie um cliente de tarefas
4. No cliente de tarefas:
   - Use `/list` para ver os clientes conectados
   - Use `/workers` para identificar os trabalhadores disponíveis
   - Submeta uma tarefa: `/calculate Worker-1234 sum 10 20 30 40`
   - Verifique o resultado quando a tarefa for concluída

## Interface Gráfica

O sistema inclui uma interface gráfica que facilita a interação com todos os componentes do sistema distribuído. A interface foi desenvolvida usando Tkinter e oferece as seguintes funcionalidades:

### Características da Interface Gráfica

- **Conexão Simplificada**: Interface para conectar-se como cliente de comunicação, cliente de tarefas ou trabalhador.
- **Visualização de Mensagens**: Exibição de mensagens recebidas e enviadas em tempo real.
- **Envio de Mensagens**: Interface para enviar mensagens de broadcast e mensagens diretas.
- **Submissão de Tarefas**: Interface para selecionar trabalhadores, tipos de tarefas e parâmetros.
- **Visualização de Resultados**: Exibição dos resultados das tarefas processadas.
- **Monitoramento de Trabalhadores**: Visualização do status e atividades dos trabalhadores.

### Como Executar a Interface Gráfica

Para iniciar a interface gráfica, execute:

```
python gui_app.py
```

A interface gráfica permite:
1. Conectar-se ao servidor como cliente, cliente de tarefas ou trabalhador
2. Visualizar e enviar mensagens
3. Submeter tarefas para processamento
4. Monitorar o processamento de tarefas
5. Visualizar resultados de tarefas

## Persistência de Dados

O sistema implementa persistência de dados usando SQLite, permitindo que informações sejam armazenadas mesmo quando o servidor é reiniciado.

### Dados Persistidos

- **Clientes**: Informações sobre clientes conectados, incluindo nome, tipo e status.
- **Mensagens**: Histórico de mensagens trocadas no sistema, incluindo mensagens de broadcast e diretas.
- **Tarefas**: Informações sobre tarefas submetidas, incluindo tipo, parâmetros, status e resultados.

### Banco de Dados

O banco de dados SQLite é gerenciado pelo módulo `db_manager.py`, que fornece uma interface para:
- Registrar e gerenciar clientes
- Armazenar e recuperar mensagens
- Armazenar informações sobre tarefas e seus resultados

O banco de dados é criado automaticamente quando o servidor é iniciado e não requer configuração adicional.

## Extensões Possíveis

O sistema ainda pode ser estendido de várias maneiras:

1. **Autenticação e Segurança**: Adicionar mecanismos de autenticação e criptografia.
2. **Balanceamento de Carga Automático**: Implementar distribuição automática de tarefas baseada na carga dos trabalhadores.
3. **Descoberta de Serviços**: Permitir que trabalhadores se registrem automaticamente no sistema.
4. **Replicação de Servidor**: Implementar múltiplos servidores para aumentar a disponibilidade.
5. **Visualização de Estatísticas**: Adicionar gráficos e estatísticas sobre o uso do sistema.

## Conclusão

Este sistema distribuído demonstra conceitos fundamentais de sistemas distribuídos em uma implementação prática e funcional. Ele pode ser usado como base para o desenvolvimento de sistemas distribuídos mais complexos ou como ferramenta educacional para entender os princípios de sistemas distribuídos.
