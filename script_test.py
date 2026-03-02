import sqlite3
import logging
import base64
from pathlib import Path

# === 1. Configurações de Caminho ===
BASE_DIR = Path(__file__).parent / "dados"
DB_PATH = BASE_DIR / "listadigital.db"
LOG_PATH = BASE_DIR / "log_bd.log"
PASTA_IMAGENS = Path(__file__).parent / "upload_teste"
HTML_OUTPUT = BASE_DIR / "visualizar_empresas.html"

BASE_DIR.mkdir(exist_ok=True)
PASTA_IMAGENS.mkdir(exist_ok=True)

# === Configuração do Logging ===
logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    encoding='utf-8'
)

# === 2. Funções de Apoio ===

def inicializar_bd():
    """Cria as tabelas se não existirem"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.execute("PRAGMA foreign_keys = ON;")
        cursor = conn.cursor()
        cursor.executescript("""
        CREATE TABLE IF NOT EXISTS Category(id TEXT PRIMARY KEY, name TEXT, slug TEXT);
        CREATE TABLE IF NOT EXISTS Workers (id TEXT PRIMARY KEY, name TEXT);
        CREATE TABLE IF NOT EXISTS COMPANY(
            id TEXT PRIMARY KEY, name TEXT UNIQUE, description TEXT,
            logoFileId TEXT, bannerFileId TEXT, categoryId TEXT, workerId TEXT,
            FOREIGN KEY (categoryId) REFERENCES Category(id),
            FOREIGN KEY (workerId) REFERENCES Workers(id)
        );
        """)
        conn.commit()
        logging.info("Banco de dados inicializado e tabelas verificadas/criadas.")
    except sqlite3.Error as e:
        logging.error(f"Erro ao inicializar banco de dados: {e}")
    finally:
        conn.close()

def setup_teste():
    """Cria os IDs necessários para as Foreign Keys"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO Category (id, name, slug) VALUES (?, ?, ?)", ("id_cat", "Alimentação", "alimentacao"))
        cursor.execute("INSERT OR IGNORE INTO Workers (id, name) VALUES (?, ?)", ("id_worker", "Mateus Rocha"))
        conn.commit()
        logging.info("Setup de teste (Category/Worker) concluído.")
    except sqlite3.Error as e:
        logging.error(f"Erro no setup de teste: {e}")
    finally:
        conn.close()

def converter_para_base64(caminho_arquivo):
    if not caminho_arquivo.exists():
        logging.warning(f"Arquivo não encontrado para conversão: {caminho_arquivo}")
        return None
    try:
        with open(caminho_arquivo, 'rb') as file:
            encoded = base64.b64encode(file.read()).decode('utf-8')
            ext = caminho_arquivo.suffix.replace('.', '')
            logging.info(f"Arquivo {caminho_arquivo.name} convertido para Base64 com sucesso.")
            return f"data:image/{ext};base64,{encoded}"
    except Exception as e:
        logging.error(f"Falha na conversão Base64 de {caminho_arquivo.name}: {e}")
        return None

def inserir_empresa_com_base64(nome_empresa, nome_logo, nome_banner):
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        string_logo = converter_para_base64(PASTA_IMAGENS / nome_logo)
        string_banner = converter_para_base64(PASTA_IMAGENS / nome_banner)
        
        sql = "INSERT OR REPLACE INTO COMPANY (id, name, logoFileId, bannerFileId, categoryId, workerId) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(sql, (nome_empresa.lower().replace(" ", "_"), nome_empresa, string_logo, string_banner, "id_cat", "id_worker"))
        
        conn.commit()
        logging.info(f"Empresa '{nome_empresa}' inserida/atualizada no banco de dados.")
        print(f"Empresa '{nome_empresa}' salva com sucesso!")
    except sqlite3.Error as e:
        logging.error(f"Erro ao inserir empresa {nome_empresa}: {e}")
    finally:
        conn.close()

def gerar_visualizacao_html():
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("SELECT name, logoFileId, bannerFileId FROM COMPANY")
        empresas = cursor.fetchall()
        
        if not empresas:
            logging.info("Geração de HTML abortada: Nenhuma empresa no banco.")
            return

        html = "<html><body style='font-family:sans-serif;'><h1>Preview Empresas</h1>"
        for nome, logo, banner in empresas:
            html += f"<div><h3>{nome}</h3><img src='{logo}' width='100'><img src='{banner}' width='300'></div><hr>"
        html += "</body></html>"
        
        with open(HTML_OUTPUT, "w", encoding="utf-8") as f:
            f.write(html)
        
        logging.info(f"Arquivo HTML de visualização gerado em: {HTML_OUTPUT}")
    except Exception as e:
        logging.error(f"Erro ao gerar visualização HTML: {e}")
    finally:
        conn.close()

# === 3. EXECUÇÃO ===

if __name__ == "__main__":
    logging.info("--- Iniciando execução do script ---")
    inicializar_bd()
    setup_teste()
    
    imagens_na_pasta = list(PASTA_IMAGENS.glob("*.*"))
    if len(imagens_na_pasta) >= 2:
        logo_teste = imagens_na_pasta[0].name
        banner_teste = imagens_na_pasta[1].name
        inserir_empresa_com_base64("Empresa Automática", logo_teste, banner_teste)
    else:
        logging.warning("Imagens insuficientes na pasta de upload para realizar o teste automático.")
    
    gerar_visualizacao_html()
    logging.info("--- Execução finalizada ---")