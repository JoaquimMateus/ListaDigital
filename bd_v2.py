import sqlite3
import logging
import base64
from pathlib import Path

# === 1. Configurações de Caminho ===
BASE_DIR = Path(__file__).parent / "dados"
DB_PATH = BASE_DIR / "listadigital.db"
LOG_PATH = BASE_DIR / "log_bd.log"
PASTA_IMAGENS = Path(__file__).parent / "upload_teste"

# Garante que as pastas existam
BASE_DIR.mkdir(exist_ok=True)
PASTA_IMAGENS.mkdir(exist_ok=True)

# === 2. Configuração do Logging ===
logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8' # Garante suporte a acentos nos logs
)

# === 3. Inicialização do Banco de Dados ===
def inicializar_bd():
    init = None
    cursor = None
    try:
        logging.info('Iniciando conexão com o SQLite para criação de tabelas.')
        init = sqlite3.connect(str(DB_PATH))
        init.execute("PRAGMA foreign_keys = ON;")
        cursor = init.cursor()

        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Page (
            id TEXT PRIMARY KEY NOT NULL,
            name TEXT UNIQUE NOT NULL,
            icon TEXT UNIQUE NOT NULL,
            colorTheme TEXT NOT NULL,
            createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
            updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS Category(
            id TEXT PRIMARY KEY NOT NULL,
            name TEXT UNIQUE NOT NULL,
            slug TEXT UNIQUE NOT NULL,
            createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
            updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS Workers (
            id TEXT PRIMARY KEY NOT NULL,
            name TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS COMPANY(
            id TEXT PRIMARY KEY NOT NULL,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            logoFileId TEXT, 
            bannerFileId TEXT,
            categoryId TEXT NOT NULL,
            workerId TEXT NOT NULL,
            createdAt DATETIME DEFAULT CURRENT_TIMESTAMP,
            updatedAt DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (categoryId) REFERENCES Category(id) ON DELETE RESTRICT,
            FOREIGN KEY (workerId) REFERENCES Workers(id) ON DELETE RESTRICT
        );
        """)
        init.commit()
        logging.info(f'Banco de dados e tabelas configurados com sucesso em: {DB_PATH}')
        print("BD configurado com sucesso!")

    except sqlite3.Error as e:
        logging.exception("Erro crítico na criação do Banco de Dados")
        print(f"Erro ao configurar BD: {e}")
    finally:
        if cursor: cursor.close()
        if init: init.close()

# === 4. Funções de Manipulação de Dados ===

def setup_teste():
    """Cria dados básicos para evitar erro de Foreign Key"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        cursor.execute("INSERT OR IGNORE INTO Category (id, name, slug) VALUES (?, ?, ?)", 
                       ("id_cat", "Alimentação", "alimentacao"))
        
        cursor.execute("INSERT OR IGNORE INTO Workers (id, name) VALUES (?, ?)", 
                       ("id_worker", "Mateus Rocha"))
        
        conn.commit()
        logging.info("Setup de teste (Categoria/Trabalhador) executado com sucesso.")
    except Exception as e:
        logging.error(f"Erro no setup de teste: {e}")
    finally:
        conn.close()

def converter_para_base64(caminho_arquivo):
    """Lê o arquivo, converte para Base64 e registra no log"""
    if not caminho_arquivo.exists():
        logging.warning(f"Tentativa de conversão falhou: Arquivo não encontrado em {caminho_arquivo}")
        return None
    
    try:
        with open(caminho_arquivo, 'rb') as file:
            bytes_arquivo = file.read()
            base64_string = base64.b64encode(bytes_arquivo).decode('utf-8')
            extensao = caminho_arquivo.suffix.replace('.', '').lower()
            if extensao == 'jpg': extensao = 'jpeg'
            
            logging.info(f"Arquivo {caminho_arquivo.name} convertido para Base64 com sucesso.")
            return f"data:image/{extensao};base64,{base64_string}"
    except Exception as e:
        logging.error(f"Erro ao processar conversão de imagem ({caminho_arquivo.name}): {e}")
        return None

def inserir_empresa_com_base64(nome_empresa, nome_logo, nome_banner):
    conn = None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()

        logging.info(f"Iniciando inserção da empresa: {nome_empresa}")

        # Conversão das imagens
        string_logo = converter_para_base64(PASTA_IMAGENS / nome_logo)
        string_banner = converter_para_base64(PASTA_IMAGENS / nome_banner)

        sql = """
        INSERT OR REPLACE INTO COMPANY (
            id, name, logoFileId, bannerFileId, categoryId, workerId
        ) VALUES (?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(sql, (
            f"id_{nome_empresa.lower().replace(' ', '_')}", 
            nome_empresa, 
            string_logo, 
            string_banner, 
            "id_cat", 
            "id_worker"
        ))
        
        conn.commit()
        print(f"Sucesso! Dados Base64 salvos para: {nome_empresa}")
        logging.info(f"Empresa '{nome_empresa}' salva com sucesso com strings Base64.")

    except Exception as e:
        logging.error(f"Falha ao inserir empresa '{nome_empresa}' no banco: {e}")
        print(f"Erro ao inserir: {e}")
    finally:
        if conn: conn.close()

# === 5. Execução ===

if __name__ == "__main__":
    logging.info("--- INÍCIO DA EXECUÇÃO DO SCRIPT ---")
    
    inicializar_bd()
    setup_teste()
    
    # Exemplo de uso automático (mude os nomes para os arquivos que você tem na pasta)
    # inserir_empresa_com_base64("Minha Empresa Teste", "logo.png", "banner.jpg")
    
    logging.info("--- FIM DA EXECUÇÃO DO SCRIPT ---")