import os
import glob
import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, DECIMAL, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# Configurações
PASTA_CSV = './dados'
ARQUIVO_DB = 'Dados Meteorologicos do Inmet.db'

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(f'sqlite:///{ARQUIVO_DB}')
Session = sessionmaker(bind=engine)

class Estacao(Base):
    __tablename__ = 'estacao'

    id = Column(Integer, primary_key=True)
    regiao = Column(String)
    uf = Column(String(2))
    nome_estacao = Column(String)
    codigo_wmo = Column(String(10))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(10, 8))
    altitude = Column(DECIMAL(10, 2))
    data_fundacao = Column(Date)

    dados = relationship("DadoMeteorologico", back_populates="estacao")


class DadoMeteorologico(Base):
    __tablename__ = 'dados_meteorologicos'

    id = Column(Integer, primary_key=True)
    estacao_id = Column(Integer, ForeignKey('estacao.id'))
    data = Column(Date)
    hora = Column(Time)
    precipitacao_total_mm = Column(DECIMAL(10, 2))
    pressao_nivel_estacao_mB = Column(DECIMAL(10, 2))
    pressao_max_ant_mB = Column(DECIMAL(10, 2))
    pressao_min_ant_mB = Column(DECIMAL(10, 2))
    radiacao_global_KJ_m2 = Column(DECIMAL(10, 2))
    temp_bulbo_seco_C = Column(DECIMAL(10, 2))
    temp_ponto_orvalho_C = Column(DECIMAL(10, 2))
    temp_max_ant_C = Column(DECIMAL(10, 2))
    temp_min_ant_C = Column(DECIMAL(10, 2))
    temp_orvalho_max_ant_C = Column(DECIMAL(10, 2))
    temp_orvalho_min_ant_C = Column(DECIMAL(10, 2))
    umidade_rel_max_ant_pct = Column(DECIMAL(10, 2))
    umidade_rel_min_ant_pct = Column(DECIMAL(10, 2))
    umidade_rel_ar_pct = Column(DECIMAL(10, 2))
    vento_direcao_graus = Column(DECIMAL(10, 2))
    vento_rajada_max_ms = Column(DECIMAL(10, 2))
    vento_velocidade_ms = Column(DECIMAL(10, 2))

    estacao = relationship("Estacao", back_populates="dados")

# Criar tabelas se não existirem
Base.metadata.create_all(engine)

# Função para converter valores e tratar -9999
def parse_valor(val):
    try:
        v = float(val.replace(",", "."))
        return None if v == -9999 else v
    except:
        return None

def processar_arquivo_csv(caminho):
    with open(caminho, 'r', encoding='latin-1') as f:
        linhas = f.readlines()

    metadados = {}
    for i in range(7):
        chave, valor = linhas[i].strip().split(";")
        chave = chave.split(":")[0].strip().lower()
        metadados[chave] = valor.strip()

    estacao = Estacao(
        regiao=metadados.get("regi�o"),
        uf=metadados.get("uf"),
        nome_estacao=metadados.get("esta��o"),
        codigo_wmo=metadados.get("codigo (wmo)"),
        latitude=parse_valor(metadados.get("latitude")),
        longitude=parse_valor(metadados.get("longitude")),
        altitude=parse_valor(metadados.get("altitude")),
        data_fundacao=datetime.strptime(metadados.get("data de funda��o (yyyy-mm-dd)"), "%Y-%m-%d").date()
    )

    # Ler os dados a partir da 8ª linha
    df = pd.read_csv(caminho, sep=";", skiprows=8, encoding='latin-1')
    df.columns = df.columns.str.strip()

    session = Session()

    # Verifica se a estação já existe
    existente = session.query(Estacao).filter_by(
        nome_estacao=estacao.nome_estacao,
        codigo_wmo=estacao.codigo_wmo
    ).first()

    if existente:
        estacao_id = existente.id
    else:
        session.add(estacao)
        session.commit()
        estacao_id = estacao.id

    for _, row in df.iterrows():
        try:
            dado = DadoMeteorologico(
                estacao_id=estacao_id,
                data=datetime.strptime(row['DATA (YYYY-MM-DD)'], "%Y-%m-%d").date(),
                hora=datetime.strptime(row['HORA (UTC)'], "%H:%M").time(),
                precipitacao_total_mm=parse_valor(row['PRECIPITA��O TOTAL, HOR�RIO (mm)']),
                pressao_nivel_estacao_mB=parse_valor(row['PRESSAO ATMOSFERICA AO NIVEL DA ESTACAO, HORARIA (mB)']),
                pressao_max_ant_mB=parse_valor(row['PRESS�O ATMOSFERICA MAX.NA HORA ANT. (AUT) (mB)']),
                pressao_min_ant_mB=parse_valor(row['PRESS�O ATMOSFERICA MIN. NA HORA ANT. (AUT) (mB)']),
                radiacao_global_KJ_m2=parse_valor(row['RADIACAO GLOBAL (KJ/m�)']),
                temp_bulbo_seco_C=parse_valor(row['TEMPERATURA DO AR - BULBO SECO, HORARIA (�C)']),
                temp_ponto_orvalho_C=parse_valor(row['TEMPERATURA DO PONTO DE ORVALHO (�C)']),
                temp_max_ant_C=parse_valor(row['TEMPERATURA M�XIMA NA HORA ANT. (AUT) (�C)']),
                temp_min_ant_C=parse_valor(row['TEMPERATURA M�NIMA NA HORA ANT. (AUT) (�C)']),
                temp_orvalho_max_ant_C=parse_valor(row['TEMPERATURA ORVALHO MAX. NA HORA ANT. (AUT) (�C)']),
                temp_orvalho_min_ant_C=parse_valor(row['TEMPERATURA ORVALHO MIN. NA HORA ANT. (AUT) (�C)']),
                umidade_rel_max_ant_pct=parse_valor(row['UMIDADE REL. MAX. NA HORA ANT. (AUT) (%)']),
                umidade_rel_min_ant_pct=parse_valor(row['UMIDADE REL. MIN. NA HORA ANT. (AUT) (%)']),
                umidade_rel_ar_pct=parse_valor(row['UMIDADE RELATIVA DO AR, HORARIA (%)']),
                vento_direcao_graus=parse_valor(row['VENTO, DIRE��O HORARIA (gr) (� (gr))']),
                vento_rajada_max_ms=parse_valor(row['VENTO, RAJADA MAXIMA (m/s)']),
                vento_velocidade_ms=parse_valor(row['VENTO, VELOCIDADE HORARIA (m/s)'])
            )
            session.add(dado)
        except Exception as e:
            print(f"Erro ao processar linha: {e}")
            continue

    session.commit()
    session.close()
    print(f"Arquivo '{os.path.basename(caminho)}' importado com sucesso.")

# Loop para processar todos os arquivos CSV
csv_files = glob.glob(os.path.join(PASTA_CSV, "*.csv"))

for arquivo in csv_files:
    processar_arquivo_csv(arquivo)
