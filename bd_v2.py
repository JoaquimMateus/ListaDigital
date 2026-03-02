import sqlite3
import logging
from pathlib import Path
import base64

# === Configurações de caminho ===
BASE_DIR = Path(__file__).parent / "dados"
DB_PATH = BASE_DIR / "listadigital.db"
LOG_PATH = BASE_DIR / "log_bd.log"
PASTA_IMAGENS = BASE_DIR / "upload_teste"

# Garante que a pasta exista
BASE_DIR.mkdir(exist_ok=True)
PASTA_IMAGENS.mkdir(exist_ok=True)

# === Logging ===
logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.info('Inicialização do Cursor e criação do BD')

init = None
cursor = None

try:
    # Conexão com o arquivo .db (não a pasta)
    init = sqlite3.connect(str(DB_PATH))
    # Ativa foreign keys (desativadas por padrão no SQLite)
    init.execute("PRAGMA foreign_keys = ON;")
    cursor = init.cursor()

    # Construção das tabelas
    cursor.executescript("""
CREATE TABLE IF NOT EXISTS Page (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT UNIQUE NOT NULL,
    icon TEXT UNIQUE NOT NULL,      -- Nome do ícone
    colorTheme TEXT NOT NULL,       -- Cor do ícone mencionada no print
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Category(
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT UNIQUE NOT NULL,
    slug TEXT UNIQUE NOT NULL,      -- Nome curto ou sigla
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS CategoryPage(
    id TEXT PRIMARY KEY NOT NULL,
    categoryId TEXT NOT NULL,
    pageId TEXT NOT NULL,
    UNIQUE(categoryId, pageId),
    FOREIGN KEY (categoryId) REFERENCES Category(id) ON DELETE CASCADE,
    FOREIGN KEY (pageId) REFERENCES Page(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Workers (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS COMPANY(
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT UNIQUE NOT NULL,
    description TEXT,

    -- Contatos e Localização
    telefone TEXT,
    whatsapp TEXT,
    email TEXT,
    website TEXT,
    endereco TEXT,        -- Localização
    instagram TEXT,
    facebook TEXT,

    -- Imagens (As duas solicitadas)
    logoFileId TEXT,     -- Logo
    bannerFileId TEXT,   -- Banner

    -- Status e Datas
    isActive INTEGER DEFAULT 1, -- Ativo (1) ou Não (0)
    createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
    updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,

    -- Relacionamentos
    categoryId TEXT NOT NULL,
    workerId TEXT NOT NULL, -- O único usuário que opera o sistema

    FOREIGN KEY (categoryId) REFERENCES Category(id) ON DELETE RESTRICT,
    FOREIGN KEY (workerId) REFERENCES Workers(id) ON DELETE RESTRICT
);

/* Triggers opcionais para atualizar updatedAt automaticamente */
CREATE TRIGGER IF NOT EXISTS trg_page_updated_at
AFTER UPDATE ON Page
FOR EACH ROW
BEGIN
    UPDATE Page SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_category_updated_at
AFTER UPDATE ON Category
FOR EACH ROW
BEGIN
    UPDATE Category SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

CREATE TRIGGER IF NOT EXISTS trg_company_updated_at
AFTER UPDATE ON COMPANY
FOR EACH ROW
BEGIN
    UPDATE COMPANY SET updatedAt = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
""")

    init.commit()
    logging.info('BD e tabelas criadas com sucesso em: %s', DB_PATH)
    print("BD configurado com sucesso em:", DB_PATH)

except sqlite3.Error as e:
    logging.exception("Erro na criação do BD")
    print(f"Erro: {e}")

finally:
    # Fecha com segurança
    try:
        if cursor is not None:
            cursor.close()
    except Exception:
        pass
    try:
        if init is not None:
            init.close()
    except Exception:
        pass


import sqlite3
from pathlib import Path

def converter_para_binario(caminho_arquivo):
    """Lê o arquivo e retorna os bytes (binário)"""
    with open(caminho_arquivo, 'rb') as file:
        return file.read()
    
def setup_teste():
    """Cria dados básicos para não dar erro de Foreign Key"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Insere uma categoria de teste
        cursor.execute("INSERT OR IGNORE INTO Category (id, name, slug) VALUES (?, ?, ?)", 
                       ("id_cat", "Alimentação", "alimentacao"))
        
        # Insere um trabalhador de teste
        cursor.execute("INSERT OR IGNORE INTO Workers (id, name) VALUES (?, ?)", 
                       ("id_worker", "Mateus Rocha"))
        
        conn.commit()
    finally:
        conn.close()

def inserir_empresa_com_fotos(nome_empresa, nome_logo, nome_banner):
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # 1. Caminhos completos das imagens
        path_logo = PASTA_IMAGENS / nome_logo
        path_banner = PASTA_IMAGENS / nome_banner

        # 2. Converte as imagens para binário (se existirem)
        blob_logo = converter_para_binario(path_logo) if path_logo.exists() else None
        blob_banner = converter_para_binario(path_banner) if path_banner.exists() else None

        # 3. Executa o INSERT
        # Nota: workerId e categoryId precisam existir antes no banco (Foreign Keys)
        sql = """
        INSERT INTO COMPANY (
            id, name, logoFileId, bannerFileId, categoryId, workerId
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        # Usando IDs genéricos para o teste (ajuste conforme seu sistema)
        cursor.execute(sql, ("id_unico_123", nome_empresa, blob_logo, blob_banner, "id_cat", "id_worker"))
        
        conn.commit()
        print(f"Empresa {nome_empresa} salva com sucesso com as imagens no BD!")

    except Exception as e:
        print(f"Erro ao inserir no banco: {e}")
    finally:
        conn.close()

# Exemplo de uso:
# Coloque arquivos chamados 'logo.png' e 'banner.jpg' na pasta 'upload_teste' no seu desktop
# inserir_empresa_com_fotos("Minha Empresa Teste", "logo.png", "banner.jpg")

def converter_para_base64(caminho_arquivo):
    """Lê o arquivo, converte para Base64 e retorna a string pronta para o HTML"""
    if not caminho_arquivo.exists():
        return None
    
    with open(caminho_arquivo, 'rb') as file:
        bytes_arquivo = file.read()
        # Converte para base64 e depois para string utf-8
        base64_string = base64.b64encode(bytes_arquivo).decode('utf-8')
        
        # Identifica a extensão para montar o cabeçalho do navegador
        extensao = caminho_arquivo.suffix.replace('.', '')
        if extensao == 'jpg': extensao = 'jpeg'
        
        # Retorna o formato que o <img src=""> entende
        return f"data:image/{extensao};base64,{base64_string}"

def inserir_empresa_com_base64(nome_empresa, nome_logo, nome_banner):
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        # 1. Converte as imagens da pasta para strings Base64
        string_logo = converter_para_base64(PASTA_IMAGENS / nome_logo)
        string_banner = converter_para_base64(PASTA_IMAGENS / nome_banner)

        # 2. Executa o INSERT
        # Agora as colunas logoFileId e bannerFileId guardarão TEXTO (a string base64)
        sql = """
        INSERT INTO COMPANY (
            id, name, logoFileId, bannerFileId, categoryId, workerId
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        # IDs de teste (lembre-se que 'id_cat' e 'id_worker' devem existir nas tabelas pai)
        cursor.execute(sql, (
            "id_teste_001", 
            nome_empresa, 
            string_logo, 
            string_banner, 
            "id_cat", 
            "id_worker"
        ))
        
        conn.commit()
        print(f"Sucesso! Dados Base64 salvos para: {nome_empresa}")

    except Exception as e:
        print(f"Erro ao inserir: {e}")
    finally:
        conn.close()