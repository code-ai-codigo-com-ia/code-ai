import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def send_message_to_openai(conversation, model):
    """Envia uma mensagem para a OpenAI usando o histórico de conversa"""
    try:
        if not conversation or len(conversation) == 0:
            raise ValueError("O array de mensagens está vazio. Por favor, forneça pelo menos uma mensagem válida.")
        
        print("Mensagem enviada para OpenAI:")
        for msg in conversation:
            print(f"{msg['role'].capitalize()}: {msg['content']}")
        print("="*50)  # Linha separadora

        # Enviar a conversa para a OpenAI usando o modelo especificado
        response = client.chat.completions.create(model=model, messages=conversation)

        # Extrair a mensagem de resposta do assistente
        assistant_message = response.choices[0].message.content

        print("Resposta recebida da OpenAI:")
        print(assistant_message)
        print("="*50)  # Linha separadora

        if hasattr(response, 'usage') and response.usage:
            token_usage = response.usage
            prompt_tokens = token_usage.prompt_tokens
            completion_tokens = token_usage.completion_tokens
            total_tokens = token_usage.total_tokens

            print("Contagem de tokens:")
            print(f"Tokens do prompt: {prompt_tokens}")
            print(f"Tokens da resposta: {completion_tokens}")
            print(f"Total de tokens usados: {total_tokens}")
            print("="*50)  # Linha separadora
        else:
            print("Informações de uso de tokens não disponíveis na resposta.")

        return assistant_message

    except Exception as e:
        raise RuntimeError(f"Erro ao enviar mensagem para OpenAI: {str(e)}")
    