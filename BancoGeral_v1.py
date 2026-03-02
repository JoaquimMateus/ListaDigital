import sqlite3
import logging

LOG_FILE_NAME = "log_bd"

logging.basicConfig(
    filename= LOG_FILE_NAME,
    level= logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logging.info(r'Inicialização do Cursor e criação do BD')
#Inicialização do BD

try:
    caminho_bd = r"C:\Users\mateus.rocha\Desktop\bd-listadigital"
    init = sqlite3.connect(caminho_bd)
    cursor = init.cursor()

#Construção das tabelas

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

""")

    init.commit()
    init.close()

    logging.info('BD e tabelas criadas com sucesso')
    print("BD configurado com sucesso")
except sqlite3.Error as e:
    logging.error(f"Erro na criação do BD")
    print(f"Erro: {e}")

finally:
    if init:
        init.close()

