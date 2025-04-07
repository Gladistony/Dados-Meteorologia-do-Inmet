from sqlalchemy import create_engine, text
from datetime import timedelta
from tqdm import tqdm
from datetime import datetime

# Conectar ao banco SQLite
engine = create_engine("sqlite:///clima.db")

def analisar_estacao(estacao_id):
    with engine.connect() as conn:
        # Obter a primeira e a última data de medição
        datas = conn.execute(text("""
            SELECT MIN(data) AS primeira, MAX(data) AS ultima
            FROM dados_meteorologicos
            WHERE estacao_id = :id
        """), {"id": estacao_id}).mappings().fetchone()

        primeira_data = datetime.strptime(datas["primeira"], "%Y-%m-%d").date()
        ultima_data = datetime.strptime(datas["ultima"], "%Y-%m-%d").date()

        # Obter o nome da estação
        estacao = conn.execute(text("""
            SELECT nome_estacao as nome
            FROM estacao
            WHERE id = :id
        """), {"id": estacao_id}).mappings().fetchone()


        print(f"📍 Estação ID: {estacao_id}")
        print(f"📍 Nome: {estacao["nome"]}")
        if not primeira_data or not ultima_data:
            print("❌ Nenhum dado encontrado para esta estação.")
            return

        print(f"📅 Período: {primeira_data} → {ultima_data}")

        # Obter registros por dia
        resultado = conn.execute(text("""
            SELECT data, COUNT(*) as num_registros
            FROM dados_meteorologicos
            WHERE estacao_id = :id
            GROUP BY data
        """), {"id": estacao_id}).mappings()

        registros_por_dia = {row["data"]: row["num_registros"] for row in resultado}

        # Verificar número total de dias
        total_dias = (ultima_data - primeira_data).days + 1
        print(f"\n📊 Total de dias no período: {total_dias}")


if __name__ == "__main__":
    try:
        estacao_id = int(input("🔢 Digite o ID da estação: "))
        analisar_estacao(estacao_id)
    except ValueError:
        print("❌ ID inválido. Use um número inteiro.")
