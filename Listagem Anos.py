from sqlalchemy import create_engine, text
from datetime import datetime
from tqdm import tqdm

# Conectar ao banco
engine = create_engine("sqlite:///clima.db")

def listar_estacoes_por_ano(ano):
    with engine.connect() as conn:
        resultado = conn.execute(text("""
            SELECT DISTINCT e.id, e.nome_estacao, e.uf
            FROM estacao e
            JOIN dados_meteorologicos d ON d.estacao_id = e.id
            WHERE strftime('%Y', d.data) = :ano
            ORDER BY e.nome_estacao
        """), {"ano": str(ano)}).mappings()

        estacoes = list(resultado)

        if not estacoes:
            print(f"❌ Nenhuma estação com dados encontrados para o ano {ano}.")
            return

        print(f"\n📍 Estações com dados no ano {ano} ({len(estacoes)} encontradas):\n")
        for estacao in tqdm(estacoes, desc="Listando estações"):
            print(f"ID: {estacao['id']} - {estacao['nome_estacao']} ({estacao['uf']})")

if __name__ == "__main__":
    try:
        ano = int(input("📅 Digite o ano desejado (ex: 2012): "))
        listar_estacoes_por_ano(ano)
    except ValueError:
        print("❌ Ano inválido. Use um número como 2005, 2010 etc.")
