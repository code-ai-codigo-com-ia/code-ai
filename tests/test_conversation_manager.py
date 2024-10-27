import os
import pytest
import yaml
from codeai.conversation_manager import (
    initialize_conversation,
    load_conversation,
    save_response,
)

@pytest.fixture
def setup_test_project(tmp_path):
    """Cria um diretório de projeto fictício para testes."""
    # Estrutura do diretório
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    
    # Cria a estrutura de diretórios e arquivos necessários
    codeai_dir = project_dir / ".codeai"
    codeai_dir.mkdir()
    config_file = codeai_dir / "config.yml"
    
    # Criação do arquivo de configuração
    config_data = {
        'modelo': 'gpt-4o-mini',
        'temperatura': 3,
    }
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f)

    # Inicializa a conversa
    system_path, conversa_path = initialize_conversation(str(project_dir))
    
    return str(project_dir), str(system_path), str(conversa_path)

def test_initialize_conversation(setup_test_project):
    project_dir, system_path, conversa_path = setup_test_project
    
    assert os.path.exists(system_path)
    assert os.path.exists(conversa_path)
    assert os.path.exists(os.path.join(conversa_path, "1_mensagem.md"))

def test_load_conversation(setup_test_project):
    project_dir, system_path, conversa_path = setup_test_project
    
    # Adicionando mensagens fictícias
    with open(os.path.join(conversa_path, "1_mensagem.md"), 'w') as f:
        f.write("Mensagem do usuário 1")

    # Salva a resposta (simulando)
    save_response(conversa_path, "Resposta do assistente 1", os.path.join(conversa_path, "1_mensagem.md"))
    
    # Altera a expectativa para 3, já que agora temos 3 entradas na conversa
    conversation = load_conversation(conversa_path, controle_de_historico=1)
    
    assert len(conversation) == 3  # Deve conter 1 mensagem de usuário, 1 resposta do assistente e 1 próximo arquivo de mensagem
    assert conversation[0]['content'] == "Mensagem do usuário 1"
    assert conversation[1]['content'] == "Resposta do assistente 1"
    assert conversation[2]['content'] == "# Escreva sua próxima mensagem aqui e salve o arquivo."

def test_save_response(setup_test_project):
    project_dir, system_path, conversa_path = setup_test_project
    
    # Simulando a salvando a resposta
    save_response(conversa_path, "Resposta do assistente 1", os.path.join(conversa_path, "1_mensagem.md"))
    
    # Verificando se o arquivo de resposta foi criado
    response_file = os.path.join(conversa_path, "1_resposta.md")
    assert os.path.exists(response_file)
    
    with open(response_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert content == "Resposta do assistente 1"
