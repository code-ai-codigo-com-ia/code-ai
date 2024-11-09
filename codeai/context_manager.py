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
    sub_section = None  # Define sub-seções específicas como 'adicionar' e 'ignorar'
    
    with open(config_path, 'r', encoding='utf-8') as config_file:
        lines = config_file.readlines()
        
        for line in lines:
            line = line.strip()
            if line.startswith("#") or not line:
                continue  # Ignora comentários e linhas vazias
            if line.startswith("pasta-raiz:"):
                context_data['pasta_raiz'] = line.split(":", 1)[1].strip()
            elif line == "[context]":
                section = "context"
                sub_section = None  # Reinicia a sub-seção ao trocar de seção
            elif line == "[estrutura]":
                section = "estrutura"
                sub_section = None
            elif line == "[outros]":
                section = "outros"
                sub_section = None
            elif line == "adicionar:":
                sub_section = "adicionar"
            elif line == "ignorar:":
                sub_section = "ignorar"
            elif sub_section == "adicionar" and section == "context":
                context_data['adicionar'].append(line)
            elif sub_section == "ignorar" and section == "context":
                context_data['ignorar'].append(line)
            elif sub_section == "adicionar" and section == "estrutura":
                context_data['estrutura_adicionar'].append(line)
            elif sub_section == "ignorar" and section == "estrutura":
                context_data['estrutura_ignorar'].append(line)
            elif section == "outros":
                context_data['outros'].append(line)
    
    return context_data


def should_ignore(file_path, ignore_patterns, root_dir):
    """Verifica se o arquivo ou diretório deve ser ignorado com base nos padrões."""
    abs_file_path = os.path.abspath(file_path)
    base_name = os.path.basename(file_path)

    for pattern in ignore_patterns:
        pattern = pattern.strip()
        if not pattern:
            continue  # Skip empty patterns

        # Verificar diretórios que terminam com "/"
        if pattern.endswith("/"):
            directory_pattern = os.path.abspath(os.path.join(root_dir, pattern.rstrip("/")))
            if abs_file_path == directory_pattern or abs_file_path.startswith(directory_pattern + os.sep):
                return True

        # Verificar subdiretórios (terminam com "/*")
        elif pattern.endswith("/*"):
            directory_pattern = os.path.abspath(os.path.join(root_dir, pattern[:-2]))
            if abs_file_path.startswith(directory_pattern + os.sep):
                return True

        # Verificar padrões de extensão (ex: "*.txt")
        elif pattern.startswith("*.") and fnmatch.fnmatch(base_name, pattern):
            return True

        # Verificar correspondência exata de nome de arquivo ou diretório
        elif fnmatch.fnmatch(base_name, pattern):
            return True

    return False


def generate_structure(root_dir):
    """Gera a estrutura de diretórios em formato de árvore usando configurações específicas da seção [estrutura]"""
    context_data = load_context(root_dir)
    estrutura_adicionar = context_data['estrutura_adicionar']
    estrutura_ignorar = context_data['estrutura_ignorar']
    structure = []
    processed_dirs = set()

    for file_path in estrutura_adicionar:
        absolute_path = os.path.join(context_data['pasta_raiz'], file_path)
        if file_path == '.':
            for dirpath, dirnames, filenames in os.walk(context_data['pasta_raiz']):
                # Ignorar pastas com base nos padrões de [estrutura]
                if should_ignore(dirpath, estrutura_ignorar, context_data['pasta_raiz']):
                    dirnames[:] = []  # Do not descend into ignored directories
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
                    if should_ignore(os.path.join(dirpath, filename), estrutura_ignorar, context_data['pasta_raiz']):
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
                    if should_ignore(dirpath, context_data['ignorar'], context_data['pasta_raiz']):
                        continue
                    filenames = [f for f in filenames if not should_ignore(os.path.join(dirpath, f), context_data['ignorar'], context_data['pasta_raiz'])]
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
            elif os.path.isfile(absolute_path) and not should_ignore(absolute_path, context_data['ignorar'], context_data['pasta_raiz']):
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
