import os
import json
import click
import yaml
from codeai.context_manager import initialize_context, create_context_file
from codeai.conversation_manager import initialize_conversation, save_response, load_conversation

CONFIG_DIR = '.codeai'
CONVERSA_DIR = 'conversa'

@click.group()
def main():
    """Comando principal do codeai"""
    pass

@main.command()
def criar():
    """Inicializa o codeai com as configurações iniciais"""
    root_dir = os.getcwd()
    config_dir = os.path.join(root_dir, CONFIG_DIR)

    # Verifica se o diretório .codeai já existe
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        click.echo(f"Diretório {config_dir} criado com sucesso.")

    # Inicializa o arquivo de configuração e a pasta de conversa
    success, message = initialize_context(root_dir)
    click.echo(message)

    # Adiciona o controle de histórico ao arquivo config.yml
    config_data = {
        'modelo': 'gpt-4',
        'temperatura': 0.7,
        'controle_de_historico': 0  # Inicia com zero
    }

    yaml_config_path = os.path.join(config_dir, 'config.yml')
    with open(yaml_config_path, 'w', encoding='utf-8') as yaml_file:
        yaml.dump(config_data, yaml_file)

    click.echo(f"Arquivo de configuração criado em {yaml_config_path}")

    # Inicializa a conversa
    system_message_path, conversa_path = initialize_conversation(root_dir)

    # Cria o arquivo de mensagem inicial
    first_message_path = os.path.join(conversa_path, '1_mensagem.md')
    if not os.path.exists(first_message_path):
        with open(first_message_path, 'w', encoding='utf-8') as f:
            f.write("# Escreva sua mensagem aqui e salve o arquivo.\n")
        click.echo(f"Arquivo de mensagem inicial criado em {first_message_path}.")
    else:
        click.echo(f"Arquivo de mensagem inicial já existe em {first_message_path}.")

    click.echo(f"Pasta de conversa e arquivo de system criados em {os.path.join(CONFIG_DIR, CONVERSA_DIR)}.")

@main.command()
def contexto():
    """Gera o arquivo de contexto sem enviar a mensagem"""
    root_dir = os.getcwd()
    try:
        context_file_path = create_context_file(root_dir)
        click.echo(f"Arquivo de contexto gerado em {context_file_path}")
    except FileNotFoundError as e:
        click.echo(str(e))

@main.command()
def enviar():
    """Envia a mensagem para a API do modelo escolhido (OpenAI ou Gemini)"""
    root_dir = os.getcwd()

    # Inicializa ou carrega a conversa
    system_message_path, conversa_path = initialize_conversation(root_dir)

    # Carrega a mensagem de system
    with open(system_message_path, 'r', encoding='utf-8') as sys_file:
        system_message = json.load(sys_file)

    # Gera o contexto e a estrutura
    context_file_path = create_context_file(root_dir)
    with open(context_file_path, 'r', encoding='utf-8') as context_file:
        context_message = context_file.read()

    # Carrega a configuração
    config_file_path = os.path.join(root_dir, CONFIG_DIR, 'config.yml')
    with open(config_file_path, 'r', encoding='utf-8') as f:
        config_data = yaml.safe_load(f)

    # Obter o valor de controle_de_historico
    controle_de_historico = config_data.get('controle_de_historico', 0)

    # Carregar a conversa com base no controle_de_historico
    conversation = load_conversation(conversa_path, controle_de_historico)

    # Adiciona system message e contexto ao array de conversa
    conversation.insert(0, {"role": "system", "content": system_message['content']})
    if context_message:
        conversation.insert(1, {"role": "system", "content": f"Contexto adicional: {context_message}"})

    # Verifica se o modelo é Gemini ou OpenAI e usa o conector correto
    if config_data.get('modelo') == 'gemini-1.5-flash':
        from codeai.gemini_connector import send_message_to_gemini
        response = send_message_to_gemini(conversation)
    else:
        from codeai.openai_connector import send_message_to_openai
        response = send_message_to_openai(conversation)

    # Salva a resposta
    message_files = sorted([f for f in os.listdir(conversa_path) if f.endswith('_mensagem.md')])
    last_user_message_file = os.path.join(conversa_path, message_files[-1])
    save_response(conversa_path, response, last_user_message_file)

if __name__ == '__main__':
    main()
