import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CONVERSA_DIR = 'conversa'
SYSTEM_FILE = 'system_message.md'  # Alterado para .md

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

def save_message(conversa_path, user_message):
    """Salva uma nova mensagem de usuário com a extensão .md"""
    message_files = sorted([f for f in os.listdir(conversa_path) if f.startswith('mensagem_')])
    if message_files:
        last_num = max([int(f.split('_')[1].split('.md')[0]) for f in message_files])
        message_num = last_num + 1
    else:
        message_num = 1

    message_file = os.path.join(conversa_path, f"mensagem_{message_num}.md")  # Alterado para .md

    with open(message_file, 'w', encoding='utf-8') as msg_file:
        msg_file.write(user_message)

    return message_file

def load_conversation(conversa_path):
    """Carrega o histórico completo da conversa"""
    conversation = []
    files = sorted(os.listdir(conversa_path))

    for file in files:
        if file.startswith("mensagem_"):
            with open(os.path.join(conversa_path, file), 'r', encoding='utf-8') as f:
                conversation.append({
                    "role": "user",
                    "content": f.read()
                })
        elif file.startswith("resposta_"):
            with open(os.path.join(conversa_path, file), 'r', encoding='utf-8') as f:
                conversation.append({
                    "role": "assistant",
                    "content": f.read()
                })

    return conversation

def send_message_to_openai(system_message, context_message, conversa_path):
    """Envia mensagem para a OpenAI com o histórico da conversa e salva a resposta em .md"""
    try:
        conversation = []

        # Adicionar o system message
        conversation.append(system_message)

        # Adicionar o contexto (se houver)
        if context_message:
            conversation.append({"role": "user", "content": context_message})

        # Carregar o histórico completo da conversa
        previous_conversation = load_conversation(conversa_path)
        conversation.extend(previous_conversation)

        # Verificar e carregar a última mensagem de usuário
        message_files = sorted([f for f in os.listdir(conversa_path) if f.endswith('_mensagem.md')])
        if not message_files:
            raise FileNotFoundError("Nenhuma mensagem encontrada para enviar.")

        last_user_message_file = os.path.join(conversa_path, message_files[-1])
        with open(last_user_message_file, 'r', encoding='utf-8') as f:
            user_message = f.read().strip()

        # Verifica se a mensagem está vazia ou contém apenas comentários
        if not user_message or user_message.startswith("#"):
            raise ValueError("A mensagem está vazia ou contém apenas comentários. Por favor, escreva uma mensagem válida.")

        # Adicionar a nova mensagem do usuário ao histórico
        conversation.append({"role": "user", "content": user_message})

        # Enviar para a API da OpenAI
        response = client.chat.completions.create(model="gpt-4o-mini", messages=conversation)

        # Salvar a resposta no arquivo correspondente
        response_num = int(os.path.basename(last_user_message_file).split('_')[0])  # Extrai o número da mensagem
        response_file = os.path.join(conversa_path, f"{response_num}_resposta.md")  # Usa o mesmo número da mensagem

        # Extrair a mensagem de resposta do assistente
        assistant_message = response.choices[0].message.content

        # Salvar a resposta
        with open(response_file, 'w', encoding='utf-8') as resp_file:
            resp_file.write(assistant_message)

        # Criar o próximo arquivo de mensagem numerado
        next_message_num = response_num + 1
        next_message_file = os.path.join(conversa_path, f"{next_message_num}_mensagem.md")
        with open(next_message_file, 'w', encoding='utf-8') as msg_file:
            msg_file.write("# Escreva sua próxima mensagem aqui e salve o arquivo.\n")

        # Registrar o histórico completo da conversa em um arquivo separado para referência
        mensagem_enviada_path = os.path.join(os.path.dirname(conversa_path), "mensagem_enviada.md")
        with open(mensagem_enviada_path, 'w', encoding='utf-8') as msg_file:
            for msg in conversation:
                role = msg['role']
                content = msg['content']
                msg_file.write(f"{role.upper()}: {content}\n\n")

        return assistant_message
    
    except Exception as e:
        raise RuntimeError(f"Erro ao enviar mensagem para OpenAI ou salvar arquivos: {str(e)}")
