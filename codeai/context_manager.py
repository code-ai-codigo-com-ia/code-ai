import os
import fnmatch

CONFIG_FILE = '.codeai_context'

def get_config_path(root_dir):
    """Retorna o caminho completo do arquivo de configuração dentro do diretório .codeai"""
    config_dir = os.path.join(root_dir, '.codeai')
    return os.path.join(config_dir, CONFIG_FILE)


def initialize_context(root_dir):
    """Inicializa o arquivo de configuração dentro da pasta .codeai se não existir."""
    config_path = get_config_path(root_dir)
    
    if os.path.exists(config_path):
        return False, f"Configuração já existente em {config_path}"
    
    # Cria o arquivo de configuração dentro da pasta .codeai
    with open(config_path, 'w', encoding='utf-8') as config_file:
        # Seção do contexto
        config_file.write("[context]\n")
        config_file.write(f"pasta-raiz: {root_dir}\n\n")
        config_file.write("adicionar:\n")
        config_file.write(".\n")  # Adiciona a raiz automaticamente
        config_file.write("# Adicione os caminhos para incluir no contexto, um por linha\n\n")
        config_file.write("ignorar:\n")
        config_file.write(".codeai/\n")
        config_file.write(".git/\n")
        config_file.write("__pycache__/\n")
        config_file.write("*.pyc\n*.pyo\n*.bin\n*.exe\n*.dll\n*.so\n*.dylib\n*.zip\n*.tar\n*.gz\n*.7z\n*.png\n*.jpg\n*.jpeg\n")
        config_file.write("# Adicione os caminhos a serem ignorados, um por linha\n\n")
        
        # Seção da estrutura
        config_file.write("[estrutura]\n")
        config_file.write("adicionar:\n")
        config_file.write(".\n")  # Adiciona a raiz automaticamente na estrutura
        config_file.write("# Adicione os caminhos para estruturar, um por linha\n\n")
        config_file.write("ignorar:\n")
        config_file.write(".codeai/\n")
        config_file.write(".git/\n")
        config_file.write("__pycache__/\n")
        config_file.write("*.pyc\n*.pyo\n*.bin\n*.exe\n*.dll\n*.so\n*.dylib\n*.zip\n*.tar\n*.gz\n*.7z\n*.png\n*.jpg\n*.jpeg\n")
        config_file.write("# Adicione os caminhos a serem ignorados, um por linha\n\n")
        
        config_file.write("[outros]\n")
        config_file.write("outros:\n")
    
    return True, f"Configuração inicializada em {config_path}"


def load_context(root_dir):
    """Carrega os contextos e arquivos a serem ignorados do arquivo de configuração"""
    config_path = get_config_path(root_dir)
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuração não encontrada em {config_path}. Execute 'codeai init' primeiro.")
    
    context_data = {
        'pasta_raiz': '',
        'adicionar': [],
        'ignorar': [],
        'estrutura_adicionar': [],
        'estrutura_ignorar': [],
        'outros': []
    }
    
    section = None
    
    with open(config_path, 'r', encoding='utf-8') as config_file:
        lines = config_file.readlines()
        
        for line in lines:
            line = line.strip()
            if line.startswith("#") or not line:
                continue  # Ignora comentários e linhas vazias
            if line.startswith("pasta-raiz:"):
                context_data['pasta_raiz'] = line.split(":", 1)[1].strip()
            elif line.startswith("[context]"):
                section = "adicionar"
            elif line.startswith("[estrutura]"):
                section = "estrutura_adicionar"
            elif line.startswith("[outros]"):
                section = "outros"
            elif line.startswith("adicionar:"):
                continue
            elif line.startswith("ignorar:"):
                if section == "adicionar":
                    section = "ignorar"
                elif section == "estrutura_adicionar":
                    section = "estrutura_ignorar"
            elif section == "adicionar":
                context_data['adicionar'].append(line)
            elif section == "ignorar":
                context_data['ignorar'].append(line)
            elif section == "estrutura_adicionar":
                context_data['estrutura_adicionar'].append(line)
            elif section == "estrutura_ignorar":
                context_data['estrutura_ignorar'].append(line)
            elif section == "outros":
                context_data['outros'].append(line)
    
    return context_data

def should_ignore(file_path, ignore_patterns):
    """Verifica se o arquivo ou diretório deve ser ignorado com base nos padrões"""
    abs_file_path = os.path.abspath(file_path)  # Caminho absoluto do arquivo

    for pattern in ignore_patterns:
        # Verifica se o padrão é um caminho absoluto
        if os.path.isabs(pattern):
            # Usa fnmatch para tratar padrões absolutos com coringas
            if fnmatch.fnmatch(abs_file_path, pattern):
                return True
        else:
            # Trata padrões globais e relativos, aplicando tanto ao caminho completo quanto ao nome do arquivo/diretório
            if fnmatch.fnmatch(file_path, pattern) or fnmatch.fnmatch(os.path.basename(file_path), pattern):
                return True
            # Adiciona verificação para padrões de diretório com /* ao final
            if pattern.endswith("/*"):
                directory_pattern = pattern[:-2]  # Remove o /* do final
                if abs_file_path.startswith(os.path.abspath(directory_pattern)):
                    return True
    
    return False

def generate_structure(root_dir):
    """Gera a estrutura de diretórios em formato de árvore"""
    context_data = load_context(root_dir)
    structure = []
    processed_dirs = set()

    for file_path in context_data['estrutura_adicionar']:
        absolute_path = os.path.join(context_data['pasta_raiz'], file_path)
        if file_path == '.':
            for dirpath, dirnames, filenames in os.walk(context_data['pasta_raiz']):
                # Ignorar pastas com base nos padrões
                if should_ignore(dirpath, context_data['estrutura_ignorar']):
                    continue
                if dirpath in processed_dirs:
                    continue
                processed_dirs.add(dirpath)  # Evita duplicatas
                # Adiciona o diretório com indentação para simular árvore
                depth = dirpath.replace(context_data['pasta_raiz'], '').count(os.sep)
                indent = ' ' * 4 * depth
                structure.append(f"{indent}{os.path.basename(dirpath)}/")
                
                # Adiciona os arquivos com indentação
                for filename in filenames:
                    if should_ignore(os.path.join(dirpath, filename), context_data['estrutura_ignorar']):
                        continue
                    file_indent = ' ' * 4 * (depth + 1)
                    structure.append(f"{file_indent}{filename}")
    
    return structure


def create_context_file(root_dir):
    """Cria um arquivo temporário contendo o conteúdo dos arquivos de contexto e da estrutura"""
    context_data = load_context(root_dir)
    context_file_path = os.path.join(root_dir, '.codeai', 'context_message.md')  # Alterado para .md
    processed_files = set()  # Evitar duplicatas

    with open(context_file_path, 'w', encoding='utf-8') as context_file:
        context_file.write(f"Pasta raiz: {context_data['pasta_raiz']}\n")
        context_file.write("Conteúdo de arquivos adicionados:\n\n")
        
        # Iterar sobre os arquivos a serem adicionados ao contexto
        for file_path in context_data['adicionar']:
            absolute_path = os.path.join(context_data['pasta_raiz'], file_path)
            
            if file_path == '.':
                for dirpath, _, filenames in os.walk(context_data['pasta_raiz']):
                    if should_ignore(dirpath, context_data['ignorar']):
                        continue
                    filenames = [f for f in filenames if not should_ignore(os.path.join(dirpath, f), context_data['ignorar'])]
                    for filename in filenames:
                        abs_file_path = os.path.join(dirpath, filename)
                        if abs_file_path in processed_files:
                            continue
                        processed_files.add(abs_file_path)  # Evita duplicatas
                        try:
                            with open(abs_file_path, 'r', encoding='utf-8') as f:
                                context_file.write(f"\n--- Conteúdo de {abs_file_path} ---\n")
                                context_file.write(f.read())
                        except UnicodeDecodeError:
                            context_file.write(f"\n--- {abs_file_path} não pôde ser lido como UTF-8 ---\n")
            elif os.path.isfile(absolute_path) and not should_ignore(absolute_path, context_data['ignorar']):
                if absolute_path in processed_files:
                    continue
                processed_files.add(absolute_path)  # Evita duplicatas
                try:
                    with open(absolute_path, 'r', encoding='utf-8') as f:
                        context_file.write(f"\n--- Conteúdo de {file_path} ---\n")
                        context_file.write(f.read())
                except UnicodeDecodeError:
                    context_file.write(f"\n--- {file_path} não pôde ser lido como UTF-8 ---\n")

        # Gera a estrutura de diretórios em formato de árvore
        structure = generate_structure(root_dir)
        context_file.write("\nEstrutura do projeto:\n\n")
        for line in structure:
            context_file.write(f"{line}\n")
    
    return context_file_path
