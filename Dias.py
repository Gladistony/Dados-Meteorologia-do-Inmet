from sqlalchemy import create_engine, text
from datetime import datetime
from tqdm import tqdm

# Conexão com o banco SQLite
engine = create_engine("sqlite:///clima.db")

def listar_dias_unicos(estacao_id):
    with engine.connect() as conn:
        resultado = conn.execute(text("""
            SELECT DISTINCT data
            FROM dados_meteorologicos
            WHERE estacao_id = :id
            ORDER BY data
        """), {"id": estacao_id}).mappings()

        dias = [row["data"] for row in resultado]

        if not dias:
            print("❌ Nenhum dia encontrado para esta estação.")
            return

        print(f"📅 Dias únicos com dados para a estação {estacao_id} ({len(dias)} dias):\n")
        for dia in tqdm(dias, desc="Listando dias"):
            print(dia)

if __name__ == "__main__":
    try:
        estacao_id = int(input("🔢 Digite o ID da estação: "))
        listar_dias_unicos(estacao_id)
    except ValueError:
        print("❌ ID inválido. Use um número inteiro.")
