from fastapi import FastAPI
from database_service import get_company_data

app = FastAPI()

@app.get("/api/empresa/{nome}")
def read_empresa(nome: str):
    dados = get_company_data(nome)
    return dados if dados else {"erro": "Não encontrado"}