import os
import json

CONVERSA_DIR = 'conversa'
SYSTEM_FILE = 'system_message.md'

def initialize_conversation(root_dir):
    """Inicializa a pasta de conversa e o arquivo de system dentro de .codeai"""
    codeai_dir = os.path.join(root_dir, '.codeai')
    conversa_path = os.path.join(codeai_dir, CONVERSA_DIR)
    os.makedirs(conversa_path, exist_ok=True)

    system_path = os.path.join(codeai_dir, SYSTEM_FILE)
    if not os.path.exists(system_path):
        with open(system_path, 'w', encoding='utf-8') as system_file:
            system_content = {
                "role": "system",
                "content": "Você é um assistente que ajuda no desenvolvimento de software."
            }
            json.dump(system_content, system_file)

    # Cria o primeiro arquivo de mensagem
    first_message_file = os.path.join(conversa_path, "1_mensagem.md")
    if not os.path.exists(first_message_file):
        with open(first_message_file, 'w', encoding='utf-8') as msg_file:
            msg_file.write("# Escreva sua mensagem aqui e salve o arquivo.\n")

    return system_path, conversa_path

def load_conversation(conversa_path):
    """Carrega o histórico completo da conversa"""
    conversation = []
    files = sorted(os.listdir(conversa_path))

    for file in files:
        if file.endswith('_mensagem.md'):
            with open(os.path.join(conversa_path, file), 'r', encoding='utf-8') as f:
                conversation.append({
                    "role": "user",
                    "content": f.read().strip()
                })
        elif file.endswith('_resposta.md'):
            with open(os.path.join(conversa_path, file), 'r', encoding='utf-8') as f:
                conversation.append({
                    "role": "assistant",
                    "content": f.read().strip()
                })

    return conversation


def save_response(conversa_path, response, last_user_message_file):
    """Salva a resposta do modelo no arquivo de resposta"""
    response_num = int(os.path.basename(last_user_message_file).split('_')[0])
    response_file = os.path.join(conversa_path, f"{response_num}_resposta.md")

    with open(response_file, 'w', encoding='utf-8') as resp_file:
        resp_file.write(response)

    # Criar o próximo arquivo de mensagem numerado
    next_message_num = response_num + 1
    next_message_file = os.path.join(conversa_path, f"{next_message_num}_mensagem.md")
    with open(next_message_file, 'w', encoding='utf-8') as msg_file:
        msg_file.write("# Escreva sua próxima mensagem aqui e salve o arquivo.\n")
