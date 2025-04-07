from sqlalchemy import create_engine, text

engine = create_engine("sqlite:///clima.db")  # ou PostgreSQL

with engine.connect() as conn:
    resultado = conn.execute(text("""
        SELECT
            id,
            nome_estacao,
            codigo_wmo,
            uf
        FROM estacao
        ORDER BY nome_estacao;
    """))

    for linha in resultado:
        print(linha)
