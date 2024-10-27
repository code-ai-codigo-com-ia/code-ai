import os
import tempfile
import pytest
from pathlib import Path
from codeai.context_manager import (
    initialize_context,
    load_context,
    should_ignore,
    generate_structure,
    create_context_file,
)

@pytest.fixture
def setup_criar_environment():
    """Configura apenas o ambiente inicial sem criar o arquivo de configuração"""
    with tempfile.TemporaryDirectory() as root_dir:
        # Cria a pasta .codeai
        codeai_dir = os.path.join(root_dir, '.codeai')
        os.makedirs(codeai_dir, exist_ok=True)
        yield root_dir  # Fornece o root_dir configurado para os testes

def test_initialize_context(setup_criar_environment):
    root_dir = setup_criar_environment
    success, message = initialize_context(root_dir)
    config_path = os.path.join(root_dir, '.codeai', '.codeai_context')
    assert success
    assert os.path.exists(config_path)
    assert "Configuração inicializada" in message

def test_load_context(setup_criar_environment):
    root_dir = setup_criar_environment
    initialize_context(root_dir)  # Cria o arquivo de configuração necessário
    context_data = load_context(root_dir)
    assert context_data['pasta_raiz'] == root_dir
    assert '.' in context_data['adicionar']
    assert '.codeai/' in context_data['ignorar']

def test_should_ignore():
    ignore_patterns = [".git/", "*.pyc", "*.bin", "subdir/"]
    
    # Passa o diretório .git/ com a barra final para coincidir com o padrão ignore_patterns
    assert should_ignore(".git/", ignore_patterns)
    assert should_ignore("file.pyc", ignore_patterns)
    assert should_ignore("subdir/file.txt", ignore_patterns)
    assert not should_ignore("file.py", ignore_patterns)
    assert not should_ignore("anotherdir/file.txt", ignore_patterns)

def test_generate_structure(setup_criar_environment):
    root_dir = setup_criar_environment
    initialize_context(root_dir)  # Cria o arquivo de configuração necessário
    os.makedirs(os.path.join(root_dir, 'dir1/subdir'))
    Path(os.path.join(root_dir, 'dir1/file1.txt')).touch()
    Path(os.path.join(root_dir, 'dir1/subdir/file2.txt')).touch()

    structure = generate_structure(root_dir)
    
    # Verifica a estrutura exata, incluindo o nome do diretório raiz temporário
    base_name = os.path.basename(root_dir)
    assert f"{base_name}/" in structure
    assert "    dir1/" in structure
    assert "        subdir/" in structure
    assert "            file2.txt" in structure
    assert "        file1.txt" in structure

def test_create_context_file(setup_criar_environment):
    root_dir = setup_criar_environment
    initialize_context(root_dir)  # Cria o arquivo de configuração necessário
    os.makedirs(os.path.join(root_dir, 'dir'))
    with open(os.path.join(root_dir, 'dir', 'file.txt'), 'w') as f:
        f.write("conteúdo do arquivo de teste")

    context_file_path = create_context_file(root_dir)

    assert os.path.exists(context_file_path)
    with open(context_file_path, 'r') as context_file:
        content = context_file.read()
        assert "Pasta raiz" in content
        assert "conteúdo do arquivo de teste" in content
        assert "Estrutura do projeto:" in content
