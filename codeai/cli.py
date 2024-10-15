import os
import json
import click
import yaml
from codeai.context_manager import initialize_context, create_context_file
from codeai.conversation_manager import initialize_conversation, send_message_to_openai, save_message

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

    config_data = {
        'modelo': 'gpt-4',
        'temperatura': 0.7,
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
    """Envia a mensagem para a API da OpenAI"""
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

    # Verifica o último arquivo de mensagem no formato {numero}_mensagem.md
    message_files = sorted([f for f in os.listdir(conversa_path) if f.endswith('_mensagem.md')])
    if not message_files:
        click.echo("Nenhuma mensagem foi encontrada.")
        return

    # Usa o último arquivo de mensagem
    last_message_file = message_files[-1]
    last_message_num = int(last_message_file.split('_')[0])  # Extrai o número da mensagem
    
    last_message_path = os.path.join(conversa_path, last_message_file)
    with open(last_message_path, 'r', encoding='utf-8') as f:
        user_message = f.read()

    # Verifica se a mensagem não está vazia ou apenas com comentários
    if not user_message.strip() or user_message.strip().startswith("#"):
        click.echo("A mensagem está vazia ou contém apenas comentários. Por favor, escreva sua mensagem.")
        return

    # Envia para a OpenAI
    response = send_message_to_openai(system_message, context_message, conversa_path)

    # Salva a resposta no arquivo correspondente {numero}_resposta.md
    response_file = os.path.join(conversa_path, f"{last_message_num}_resposta.md")
    with open(response_file, 'w', encoding='utf-8') as resp_file:
        resp_file.write(response)
    
    click.echo(f"Resposta salva em {response_file}.")

    # Cria o próximo arquivo de mensagem numerado
    next_message_num = last_message_num + 1
    next_message_path = os.path.join(conversa_path, f"{next_message_num}_mensagem.md")

    with open(next_message_path, 'w', encoding='utf-8') as f:
        f.write("# Escreva sua próxima mensagem aqui e salve o arquivo.\n")
    click.echo(f"Arquivo {next_message_path} recriado para novas mensagens.")


if __name__ == '__main__':
    main()
