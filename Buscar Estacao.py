from sqlalchemy import create_engine, text

# Banco SQLite local
engine = create_engine("sqlite:///clima.db")

def buscar_estacao_por_nome(parte_nome):
    query = text("""
        SELECT
            id,
            nome_estacao,
            codigo_wmo,
            uf,
            regiao,
            latitude,
            longitude,
            altitude,
            data_fundacao
        FROM estacao
        WHERE LOWER(nome_estacao) LIKE :busca
        ORDER BY nome_estacao;
    """)

    with engine.connect() as conn:
        resultado = conn.execute(query, {"busca": f"%{parte_nome.lower()}%"})
        estacoes = resultado.fetchall()
        for estacao in estacoes:
            print(estacao)

estacao = input("Digite parte do nome da estação: ")
buscar_estacao_por_nome(estacao)
