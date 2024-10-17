import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def send_message_to_openai(conversation):
    """Envia uma mensagem para a OpenAI usando o histórico de conversa"""
    try:
        # Verifique se o array de conversa está vazio ou não tem formato correto
        if not conversation or len(conversation) == 0:
            raise ValueError("O array de mensagens está vazio. Por favor, forneça pelo menos uma mensagem válida.")
        
         # Imprime a conversa que será enviada
        print("Mensagem enviada para OpenAI:")
        for msg in conversation:
            print(f"{msg['role'].capitalize()}: {msg['content']}")
        print("="*50)  # Linha separadora

        # Enviar a conversa para a OpenAI
        response = client.chat.completions.create(model="gpt-4o-mini", messages=conversation)

        # Extrair a mensagem de resposta do assistente
        assistant_message = response.choices[0].message.content

        print("Resposta recebida da OpenAI:")
        print(assistant_message)
        print("="*50)  # Linha separadora

        return assistant_message

    except Exception as e:
        raise RuntimeError(f"Erro ao enviar mensagem para OpenAI: {str(e)}")
