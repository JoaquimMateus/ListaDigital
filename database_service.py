import sqlite3
from pathlib import Path

# Ajuste para o caminho onde seu .db está
DB_PATH = Path(__file__).parent / "dados" / "listadigital.db"

def get_company_data(company_name):
    """Retorna um dicionário com os dados e a logo em Base64"""
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM COMPANY WHERE name = ?", (company_name,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    finally:
        if conn: conn.close()