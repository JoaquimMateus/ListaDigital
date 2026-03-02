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

# === 2. Funções de Apoio ===

def inicializar_bd():
    """Cria as tabelas se não existirem"""
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
    conn.close()

def setup_teste():
    """Cria os IDs necessários para as Foreign Keys"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO Category (id, name, slug) VALUES (?, ?, ?)", ("id_cat", "Alimentação", "alimentacao"))
    cursor.execute("INSERT OR IGNORE INTO Workers (id, name) VALUES (?, ?)", ("id_worker", "Mateus Rocha"))
    conn.commit()
    conn.close()

def converter_para_base64(caminho_arquivo):
    if not caminho_arquivo.exists(): return None
    with open(caminho_arquivo, 'rb') as file:
        encoded = base64.b64encode(file.read()).decode('utf-8')
        ext = caminho_arquivo.suffix.replace('.', '')
        return f"data:image/{ext};base64,{encoded}"

def inserir_empresa_com_base64(nome_empresa, nome_logo, nome_banner):
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        string_logo = converter_para_base64(PASTA_IMAGENS / nome_logo)
        string_banner = converter_para_base64(PASTA_IMAGENS / nome_banner)
        
        sql = "INSERT OR REPLACE INTO COMPANY (id, name, logoFileId, bannerFileId, categoryId, workerId) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(sql, (nome_empresa.lower().replace(" ", "_"), nome_empresa, string_logo, string_banner, "id_cat", "id_worker"))
        conn.commit()
        print(f"Empresa '{nome_empresa}' salva com sucesso!")
    finally:
        conn.close()

def gerar_visualizacao_html():
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("SELECT name, logoFileId, bannerFileId FROM COMPANY")
    empresas = cursor.fetchall()
    
    if not empresas:
        print("Nenhuma empresa encontrada no banco de dados.")
        return

    html = "<html><body style='font-family:sans-serif;'><h1>Preview Empresas</h1>"
    for nome, logo, banner in empresas:
        html += f"<div><h3>{nome}</h3><img src='{logo}' width='100'><img src='{banner}' width='300'></div><hr>"
    html += "</body></html>"
    
    with open(HTML_OUTPUT, "w", encoding="utf-8") as f: f.write(html)
    print(f"Arquivo HTML gerado em: {HTML_OUTPUT}")
    conn.close()

# === 3. EXECUÇÃO EM ORDEM ===

if __name__ == "__main__":
    # 1. Cria tabelas
    inicializar_bd()
    
    # 2. Cria Categoria e Worker (evita erro de NameError e ForeignKey)
    setup_teste()
    
    # 3. Varre a pasta de imagens e tenta cadastrar algo automaticamente
    imagens_na_pasta = list(PASTA_IMAGENS.glob("*.*"))
    if len(imagens_na_pasta) >= 2:
        # Pega as duas primeiras imagens que encontrar na pasta para o teste
        logo_teste = imagens_na_pasta[0].name
        banner_teste = imagens_na_pasta[1].name
        inserir_empresa_com_base64("Empresa Automática", logo_teste, banner_teste)
    else:
        print(f"Atenção: Coloque pelo menos 2 imagens em {PASTA_IMAGENS} para o teste.")

    # 4. Gera o HTML final
    gerar_visualizacao_html()