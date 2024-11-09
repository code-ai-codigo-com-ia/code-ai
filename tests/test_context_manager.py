import os
import tempfile
import pytest
import logging
from pathlib import Path
from codeai.context_manager import (
    initialize_context,
    load_context,
    should_ignore,
    generate_structure,
    create_context_file,
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

    assert success, f"Expect success but got failure with message: {message}"
    assert os.path.exists(config_path)
    
    # Verificar se ambos os contextos possuem os padrões de ignorar comum
    with open(config_path, 'r', encoding='utf-8') as config_file:
        content = config_file.read()
        common_patterns = [
            ".codeai/",
            ".git/",
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            "*.bin",
            "*.exe",
            "*.dll",
            "*.so",
            "*.dylib",
            "*.zip",
            "*.tar",
            "*.gz",
            "*.7z",
            "*.png",
            "*.jpg",
            "*.jpeg",
            "target/",
            "*.class",
            "*.jar",
            "*.war",
            ".idea/",
            "*.iml",
            "*.gradle",
            "*.log",
            "*.gem",
            "log/",
            "tmp/",
            "vendor/",
            "*.rbc",
            ".bundle/",
            "*.sqlite3",
            ".rspec",
            "bin/",
            "pkg/",
            "vendor/",
            "*.test",
            "*.mod",
            "*.sum",
            "node_modules/",
            "package-lock.json",
            "npm-debug.log",
            ".env",
            ".npm/"
        ]

        for pattern in common_patterns:
            assert pattern in content, f"{pattern} is missing in the configuration"

def test_load_context(setup_criar_environment):
    root_dir = setup_criar_environment
    initialize_context(root_dir)  # Cria o arquivo de configuração necessário
    context_data = load_context(root_dir)

    # Verifique se ambos context e estrutura têm os mesmos padrões na seção ignorar
    expected_ignore_patterns = [
        ".codeai/",
        ".git/",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        "*.bin",
        "*.exe",
        "*.dll",
        "*.so",
        "*.dylib",
        "*.zip",
        "*.tar",
        "*.gz",
        "*.7z",
        "*.png",
        "*.jpg",
        "*.jpeg",
        "target/",
        "*.class",
        "*.jar",
        "*.war",
        ".idea/",
        "*.iml",
        "*.gradle",
        "*.log",
        "*.gem",
        "log/",
        "tmp/",
        "vendor/",
        "*.rbc",
        ".bundle/",
        "*.sqlite3",
        ".rspec",
        "bin/",
        "pkg/",
        "vendor/",
        "*.test",
        "*.mod",
        "*.sum",
        "node_modules/",
        "package-lock.json",
        "npm-debug.log",
        ".env",
        ".npm/"
    ]

    assert context_data['ignorar'] == expected_ignore_patterns
    assert context_data['estrutura_ignorar'] == expected_ignore_patterns
    
def test_should_ignore():
    ignore_patterns = [".git/", "*.pyc", "*.bin", "subdir/"]
    root_dir = "/fake/root"

    logger.info(f"Padrões de ignorar usados: {ignore_patterns}")

    assert should_ignore("/fake/root/.git/", ignore_patterns, root_dir)
    assert should_ignore("/fake/root/file.pyc", ignore_patterns, root_dir)
    assert should_ignore("/fake/root/subdir/file.txt", ignore_patterns, root_dir)
    assert not should_ignore("/fake/root/file.py", ignore_patterns, root_dir)
    assert not should_ignore("/fake/root/anotherdir/file.txt", ignore_patterns, root_dir)

def test_generate_structure(setup_criar_environment):
    root_dir = setup_criar_environment
    initialize_context(root_dir)  # Cria o arquivo de configuração necessário
    os.makedirs(os.path.join(root_dir, 'dir1/subdir'))
    Path(os.path.join(root_dir, 'dir1/file1.txt')).touch()
    Path(os.path.join(root_dir, 'dir1/subdir/file2.txt')).touch()

    structure = generate_structure(root_dir)
    
    logger.info(f"Estrutura gerada para o diretório {root_dir}:\n{structure}")
    
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

    logger.info(f"Arquivo de contexto criado em {context_file_path}")
    
    assert os.path.exists(context_file_path)
    with open(context_file_path, 'r') as context_file:
        content = context_file.read()
        
        logger.info(f"Conteúdo do arquivo de contexto:\n{content}")
        
        assert "Pasta raiz" in content
        assert "conteúdo do arquivo de teste" in content
        assert "Estrutura do projeto:" in content

@pytest.fixture
def setup_complex_environment():
    """Configura um diretório de testes complexo com vários arquivos e subdiretórios."""
    with tempfile.TemporaryDirectory() as root_dir:
        codeai_dir = os.path.join(root_dir, '.codeai')
        os.makedirs(codeai_dir, exist_ok=True)
        
        # Criar arquivos e diretórios diferentes
        os.makedirs(os.path.join(root_dir, 'dir1/subdir1'), exist_ok=True)
        os.makedirs(os.path.join(root_dir, 'dir2'), exist_ok=True)
        
        # Criar arquivos de teste
        with open(os.path.join(root_dir, 'dir1/file1.py'), 'w') as f:
            f.write("# Teste de arquivo Python")
        with open(os.path.join(root_dir, 'dir1/file2.txt'), 'w') as f:
            f.write("Texto para ignorar")
        with open(os.path.join(root_dir, 'dir1/subdir1/file3.pyc'), 'w') as f:
            f.write("# Arquivo Python Compilado")
        with open(os.path.join(root_dir, 'dir2/file4.md'), 'w') as f:
            f.write("# Arquivo Markdown")
        
        # Criar o arquivo .codeai_context com '*.txt' em ignorar
        config_path = os.path.join(codeai_dir, '.codeai_context')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("[context]\n")
            f.write(f"pasta-raiz: {root_dir}\n\n")
            f.write("adicionar:\n")
            f.write(".\n\n")
            f.write("ignorar:\n")
            f.write(".codeai/\n")
            f.write(".git/\n")
            f.write("__pycache__/\n")
            f.write("*.pyc\n")
            f.write("*.pyo\n")
            f.write("*.bin\n")
            f.write("*.exe\n")
            f.write("*.dll\n")
            f.write("*.so\n")
            f.write("*.dylib\n")
            f.write("*.zip\n")
            f.write("*.tar\n")
            f.write("*.gz\n")
            f.write("*.7z\n")
            f.write("*.png\n")
            f.write("*.jpg\n")
            f.write("*.jpeg\n")
            f.write("*.txt\n") 
            f.write("\n")
            
            # Seção [estrutura]
            f.write("[estrutura]\n")
            f.write("adicionar:\n")
            f.write(".\n\n")
            f.write("ignorar:\n")
            f.write(".codeai/\n")
            f.write(".git/\n")
            f.write("__pycache__/\n")
            f.write("*.pyc\n")
            f.write("*.pyo\n")
            f.write("*.bin\n")
            f.write("*.exe\n")
            f.write("*.dll\n")
            f.write("*.so\n")
            f.write("*.dylib\n")
            f.write("*.zip\n")
            f.write("*.tar\n")
            f.write("*.gz\n")
            f.write("*.7z\n")
            f.write("*.png\n")
            f.write("*.jpg\n")
            f.write("*.jpeg\n")
            f.write("*.txt\n")  # Também na seção [estrutura], se necessário
            f.write("\n")
            
            # Seção [outros]
            f.write("[outros]\n")
            f.write("outros:\n")

        yield root_dir  # Retorna o diretório criado

def test_various_ignore_patterns(setup_complex_environment):
    root_dir = setup_complex_environment
    # Não chamamos initialize_context aqui porque já temos um .codeai_context personalizado
    context_data = load_context(root_dir)
    ignore_patterns = context_data['ignorar']

    # Verifica se diretórios e arquivos ignorados seguem o padrão esperado
    logger.info(f"Testando com padrões: {ignore_patterns}")

    assert not should_ignore(os.path.join(root_dir, 'dir1/file1.py'), ignore_patterns, root_dir), "file1.py não deveria ser ignorado"
    assert should_ignore(os.path.join(root_dir, 'dir1/file2.txt'), ignore_patterns, root_dir), "file2.txt deveria ser ignorado"
    assert should_ignore(os.path.join(root_dir, 'dir1/subdir1/file3.pyc'), ignore_patterns, root_dir), "file3.pyc deveria ser ignorado"
    assert should_ignore(os.path.join(root_dir, '.git/config'), ignore_patterns, root_dir), ".git/config deveria ser ignorado"
    assert should_ignore(os.path.join(root_dir, '.codeai/context'), ignore_patterns, root_dir), ".codeai/context deveria ser ignorado"

def test_ignore_based_on_extension(setup_complex_environment):
    root_dir = setup_complex_environment
    # Não chamamos initialize_context aqui porque já temos um .codeai_context personalizado
    context_data = load_context(root_dir)
    ignore_patterns = context_data['ignorar']

    # Testa a ignorância baseada em extensão
    assert should_ignore(os.path.join(root_dir, 'dir1/file2.txt'), ignore_patterns, root_dir) == True
    assert should_ignore(os.path.join(root_dir, 'dir1/file1.py'), ignore_patterns, root_dir) == False
    assert should_ignore(os.path.join(root_dir, 'dir1/subdir1/file3.pyc'), ignore_patterns, root_dir) == True
    assert should_ignore(os.path.join(root_dir, 'dir2/file4.md'), ignore_patterns, root_dir) == False

def test_validation_file_and_structure(setup_complex_environment):
    root_dir = setup_complex_environment
    # Não chamamos initialize_context aqui porque já temos um .codeai_context personalizado
    context_data = load_context(root_dir)

    # Verifica se a estrutura reflete apenas a seção [estrutura]
    structure = generate_structure(root_dir)
    
    logger.info(f"Estrutura gerada: {structure}")
    
    assert any("dir1/" in line for line in structure), "Estrutura não contém 'dir1/'"
    assert any("dir2/" in line for line in structure), "Estrutura não contém 'dir2/'"
    assert any("file4.md" in line for line in structure), "Estrutura não contém 'file4.md'"
