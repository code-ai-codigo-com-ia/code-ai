import os
import json
import yaml

CONVERSA_DIR = 'conversa'
SYSTEM_FILE = 'system_message.md'
CONFIG_FILE = 'config.yml'

def load_config(root_dir):
    """Carrega as configurações do arquivo config.yml"""
    config_path = os.path.join(root_dir, '.codeai', CONFIG_FILE)
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def load_conversation(conversa_path, controle_de_historico):
    """Carrega o histórico da conversa com base no controle de histórico"""
    conversation = []
    files = sorted(os.listdir(conversa_path), key=lambda f: int(f.split('_')[0]))

    # Pega o número da última interação para limitar o histórico carregado
    current_interaction_num = int(files[-1].split('_')[0])

    # Verifica o limite de histórico a ser carregado
    if controle_de_historico >= current_interaction_num:
        # Carrega todo o histórico se controle_de_historico >= número atual da interação
        for file in files:
            file_path = os.path.join(conversa_path, file)
            if file.endswith('_mensagem.md'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    conversation.append({
                        "role": "user",
                        "content": f.read().strip()
                    })
            elif file.endswith('_resposta.md'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    conversation.append({
                        "role": "assistant",
                        "content": f.read().strip()
                    })
    else:
        # Carrega apenas o histórico limitado pelo controle_de_historico
        start_idx = max(0, len(files) - 2 * controle_de_historico - 1)
        for file in files[start_idx:]:
            file_path = os.path.join(conversa_path, file)
            if file.endswith('_mensagem.md'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    conversation.append({
                        "role": "user",
                        "content": f.read().strip()
                    })
            elif file.endswith('_resposta.md'):
                with open(file_path, 'r', encoding='utf-8') as f:
                    conversation.append({
                        "role": "assistant",
                        "content": f.read().strip()
                    })

    return conversation

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

def save_response(conversa_path, response, last_user_message_file):
    """Salva a resposta do modelo no arquivo de resposta e cria o próximo arquivo de mensagem"""
    response_num = int(os.path.basename(last_user_message_file).split('_')[0])
    response_file = os.path.join(conversa_path, f"{response_num}_resposta.md")
    
    # Verifique se o arquivo de resposta já existe; se existir, use o próximo número
    while os.path.exists(response_file):
        response_num += 1
        response_file = os.path.join(conversa_path, f"{response_num}_resposta.md")

    with open(response_file, 'w', encoding='utf-8') as resp_file:
        resp_file.write(response)

    print(f"[LOG] Resposta salva no arquivo: {response_file}")

    # Criar o próximo arquivo de mensagem numerado
    next_message_num = response_num + 1
    next_message_file = os.path.join(conversa_path, f"{next_message_num}_mensagem.md")
    
    # Sempre cria o próximo arquivo, independentemente de ser mensagem 9 ou qualquer outra
    with open(next_message_file, 'w', encoding='utf-8') as msg_file:
        msg_file.write("# Escreva sua próxima mensagem aqui e salve o arquivo.\n")
    
    print(f"[LOG] Próximo arquivo de mensagem criado: {next_message_file}")
