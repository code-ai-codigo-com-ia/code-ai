# CodeAI

CodeAI é uma ferramenta de linha de comando (CLI) que permite interagir com a API da OpenAI de maneira simples e eficiente. Ele gerencia conversas, contextos e processos de envio de mensagens, além de armazenar o histórico de interações.

## Requisitos

- **Python**: O CodeAI requer Python 3.6 ou superior. Você pode baixar a versão mais recente do Python [aqui](https://www.python.org/downloads/).

Certifique-se de que o Python esteja instalado corretamente executando o seguinte comando no terminal:

```bash
python --version
```

### Instalando o `pip`

Se você não tiver o `pip` instalado, você pode instalá-lo seguindo estas instruções:

- **Windows**:

  O `pip` geralmente é incluído na instalação do Python. Se você não tiver, execute o seguinte comando no terminal para instalar o `get-pip.py`:

  ```bash
  curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
  python get-pip.py
  ```

- **Ubuntu**:

  No Ubuntu ou outras distribuições Debian, você pode instalar o `pip` com o seguinte comando:

  ```bash
  sudo apt update
  sudo apt install python3-pip
  ```

### Verificando a Instalação do `pip`

Após a instalação, verifique se o `pip` foi instalado corretamente executando:

```bash
pip --version
```

## Estrutura do Projeto

```
code-ai/
├── setup.py                 
├── codeai.egg-info/         
├── codeai/                  
│   ├── __init__.py          
│   ├── conversation_manager.py 
│   ├── cli.py               
│   └── context_manager.py    
├── .codeai/                 
├── conversa/                
└── .git/                    
```

## Instalação

Para instalar o CodeAI, clone este repositório e instale as dependências necessárias:

```bash
git clone <URL_DO_REPOSITORIO>
cd code-ai
pip install -e .
```

## Configuração da Chave da API

### Windows

No Windows, você pode configurar sua chave de API do OpenAI usando o seguinte comando no terminal (CMD ou PowerShell):

```bash
setx OPENAI_API_KEY "sua_chave_aqui"
```

### Ubuntu

No Ubuntu, você pode configurar sua chave de API usando o seguinte comando:

```bash
export OPENAI_API_KEY="sua_chave_aqui"
```

Para garantir que essa configuração persista após reinicializações, adicione a linha acima ao seu arquivo `~/.bashrc` ou `~/.bash_profile`.

## Criando um Ambiente Virtual (Opcional)

É uma boa prática usar um ambiente virtual para gerenciar dependências de projetos Python. Siga os passos abaixo para criar e ativar um ambiente virtual:

### Criando um Ambiente Virtual

1. Navegue até a pasta do projeto:

   ```bash
   cd /caminho/para/seu/projeto/code-ai
   ```

2. Crie um ambiente virtual:

   ```bash
   python -m venv venv
   ```

### Ativando o Ambiente Virtual

- **Windows**:

   ```bash
   venv\Scripts\activate
   ```

- **Ubuntu**:

   ```bash
   source venv/bin/activate
   ```

Após ativar o ambiente virtual, instale o CodeAI seguindo as instruções da seção de instalação. Você verá que os pacotes Python agora são instalados apenas nesse ambiente.

## Inicialização e Configuração

Após a instalação, é necessário inicializar o ambiente de configuração. Execute o seguinte comando:

```bash
codeai init
```

Isso criará um diretório `.codeai` com os arquivos de configuração e um diretório `conversa` para armazenar as interações.

## Comandos

O CodeAI possui os seguintes comandos para interagir com a ferramenta:

### `codeai init`

Inicializa o CodeAI e cria a estrutura de diretórios necessária.

- **Passo a Passo**:
  1. Cria a pasta `.codeai` no diretório atual.
  2. Inicializa um arquivo de configuração com as diretrizes do contexto.
  3. Cria um diretório `conversa` para armazenar o histórico de mensagens.
  4. Cria um arquivo `1_mensagem.md` onde você pode escrever sua primeira mensagem.

### `codeai contexto`

Gera um arquivo temporário contendo o contexto atual do projeto e a estrutura de diretórios.

- **Passo a Passo**:
  1. Carrega as configurações do projeto.
  2. Gera um arquivo `.md` com o conteúdo dos arquivos que estão sendo adicionados ao contexto.
  3. O arquivo gerado pode ser usado para entender o estado atual do projeto e as interações.

### `codeai enviar`

Envia mensagens para a API da OpenAI. Este comando irá:

1. Carregar a mensagem de sistema.
2. Carregar o contexto.
3. Ler a mensagem do usuário do arquivo `nova_mensagem.txt`.
4. Salvar o histórico de mensagens e a resposta do assistente.

- **Passo a Passo**:
  1. Coloque sua mensagem em `nova_mensagem.txt` na pasta `conversa/`.
  2. Execute o comando `codeai enviar` para processar a mensagem.
  3. A resposta do assistente será salva em um arquivo no formato `{numero}_resposta.md`.
  4. O próximo arquivo de mensagens é criado automaticamente para futuras interações.

## Como Usar

1. **Inicialização e Configuração**:
   - Após clonar o repositório, execute `codea criar` para configurar o ambiente.
   - Isso criará todos os diretórios e arquivos necessários para que você comece a interagir com a API.

2. **Enviar Mensagens**:
   - Edite o arquivo `1_mensagem.md` ou crie arquivos adicionais na pasta `conversa/` para escrever suas mensagens.
   - Utilize o comando `codeai enviar` para enviar suas mensagens ao assistente da OpenAI.

3. **Verificar Respostas**:
   - As respostas do assistente são salvas na mesma pasta, com o formato `{numero}_resposta.md`, mantendo um histórico de suas interações.

## Descrição Técnica dos Métodos

### `initialize_conversation(root_dir)`

- **Função**: Inicializa a estrutura necessária para as conversas e cria arquivos de configuração.
- **Parâmetros**:
  - `root_dir`: Diretório raiz onde o projeto está localizado.
- **Retorno**: O caminho do arquivo de sistema e o diretório de conversas.

### `save_message(conversa_path, user_message)`

- **Função**: Salva uma nova mensagem do usuário em um arquivo com a extensão `.md` numerado sequencialmente.
- **Parâmetros**:
  - `conversa_path`: Caminho onde as mensagens estão armazenadas.
  - `user_message`: Mensagem do usuário a ser salva.

### `load_conversation(conversa_path)`

- **Função**: Carrega todo o histórico da conversa, juntando mensagens do usuário e respostas do assistente.
- **Parâmetros**:
  - `conversa_path`: Caminho das mensagens salvas.
- **Retorno**: Lista de dicionários representando a conversa.

### `send_message_to_openai(system_message, context_message, conversa_path)`

- **Função**: Envia uma mensagem para a OpenAI, incluindo o histórico da conversa e salva a resposta.
- **Parâmetros**:
  - `system_message`: Mensagem de contexto que define o comportamento da IA.
  - `context_message`: Mensagem de contexto adicional para fornecer mais detalhes.
  - `conversa_path`: Caminho onde as mensagens são armazenadas.

## Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para abrir um problema ou enviar um pull request.

## Licença

Esse projeto está sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## Contato

Para suporte ou consultas, entre em contato com o autor: codeai-brasil (email: codeai-brasil@proton.me).

### Notas

1. **Substitua `<URL_DO_REPOSITORIO>`** pela URL real do seu repositório.
2. **Adicione informações sobre a licença**, se aplicável, e qualquer outra informação que você acha que seria útil para os usuários e desenvolvedores que queiram contribuir ou usar seu código.
3. Você pode incluir exemplos de saída ou mais detalhes conforme achar necessário.
