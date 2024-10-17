import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def send_message_to_gemini(conversation):
    """Envia uma mensagem para o modelo Gemini usando o histórico da conversa"""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        full_conversation = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in conversation])

        print("Mensagem enviada para o Gemini:")
        print(full_conversation)
        print("="*50)  # Linha separadora

        # Enviar a mensagem concatenada para o modelo
        response = model.generate_content(full_conversation)

        print("Resposta recebida do Gemini:")
        print(response.text)
        print("="*50)  # Linha separadora

        
        return response.text

    except Exception as e:
        raise RuntimeError(f"Erro ao enviar mensagem para Gemini: {str(e)}")
