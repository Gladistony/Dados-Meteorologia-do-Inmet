import os
import zipfile
import tempfile
import glob
import pandas as pd
from tqdm import tqdm
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, DECIMAL, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime

# Configurações
PASTA_ZIP = './dados'
ARQUIVO_DB = 'clima.db'

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(f'sqlite:///{ARQUIVO_DB}')
Session = sessionmaker(bind=engine)

# Modelos
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

# Criar tabelas no banco
Base.metadata.create_all(engine)

# Funções auxiliares
def parse_valor(val):
    try:
        v = float(str(val).replace(",", "."))
        return None if v == -9999 else v
    except:
        return None

def processar_csv(caminho):
    with open(caminho, 'r', encoding='latin-1') as f:
        linhas = f.readlines()

    # Metadados (por posição)
    try:
        regiao = linhas[0].split(";")[1].strip()
        uf = linhas[1].split(";")[1].strip()
        nome_estacao = linhas[2].split(";")[1].strip()
        codigo_wmo = linhas[3].split(";")[1].strip()
        latitude = parse_valor(linhas[4].split(";")[1].strip())
        longitude = parse_valor(linhas[5].split(";")[1].strip())
        altitude = parse_valor(linhas[6].split(";")[1].strip())
        data_fundacao_str = linhas[7].split(";")[1].strip()
        #Verificar se a data_fundacao_str tem - ou /
        if "-" in data_fundacao_str:
            data_fundacao = datetime.strptime(data_fundacao_str, "%Y-%m-%d").date()
        else:
            data_fundacao = datetime.strptime(data_fundacao_str, "%d/%m/%y").date()
    except Exception as e:
        print(f"Erro ao ler metadados em {os.path.basename(caminho)}: {e}")
        return

    estacao = Estacao(
        regiao=regiao,
        uf=uf,
        nome_estacao=nome_estacao,
        codigo_wmo=codigo_wmo,
        latitude=latitude,
        longitude=longitude,
        altitude=altitude,
        data_fundacao=data_fundacao
    )

    try:
        df = pd.read_csv(caminho, sep=";", skiprows=9, header=None, encoding='latin-1')
    except Exception as e:
        print(f"Erro ao ler dados CSV: {e}")
        return

    session = Session()

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
            if "/" in str(row.iloc[0]):
                dt = datetime.strptime(row.iloc[0], "%Y/%m/%d").date()
            else:
                dt = datetime.strptime(row.iloc[0], "%Y-%m-%d").date()
            
            if "UTC" in str(row.iloc[1]):
                hr = row.iloc[1].split(" ")[0]
                hr = datetime.strptime(hr, "%H%M").time()
            else:
                hr = datetime.strptime(row.iloc[1], "%H:%M").time()
            dado = DadoMeteorologico(
                estacao_id=estacao_id,
                data=dt,
                hora=hr,
                precipitacao_total_mm=parse_valor(row.iloc[2]),
                pressao_nivel_estacao_mB=parse_valor(row.iloc[3]),
                pressao_max_ant_mB=parse_valor(row.iloc[4]),
                pressao_min_ant_mB=parse_valor(row.iloc[5]),
                radiacao_global_KJ_m2=parse_valor(row.iloc[6]),
                temp_bulbo_seco_C=parse_valor(row.iloc[7]),
                temp_ponto_orvalho_C=parse_valor(row.iloc[8]),
                temp_max_ant_C=parse_valor(row.iloc[9]),
                temp_min_ant_C=parse_valor(row.iloc[10]),
                temp_orvalho_max_ant_C=parse_valor(row.iloc[11]),
                temp_orvalho_min_ant_C=parse_valor(row.iloc[12]),
                umidade_rel_max_ant_pct=parse_valor(row.iloc[13]),
                umidade_rel_min_ant_pct=parse_valor(row.iloc[14]),
                umidade_rel_ar_pct=parse_valor(row.iloc[15]),
                vento_direcao_graus=parse_valor(row.iloc[16]),
                vento_rajada_max_ms=parse_valor(row.iloc[17]),
                vento_velocidade_ms=parse_valor(row.iloc[18])
            )
            session.add(dado)
        except Exception as e:
            print(f"⚠️ Erro ao processar linha: {e}")
            continue

    session.commit()
    session.close()

# Processar todos os zips da pasta
zip_files = glob.glob(os.path.join(PASTA_ZIP, "*.zip"))

if not zip_files:
    print("❌ Nenhum arquivo ZIP encontrado na pasta 'dados'")
else:
    print(f"🔍 {len(zip_files)} arquivo(s) ZIP encontrado(s). Processando...\n")

    for zip_file in tqdm(zip_files, desc="ZIPs", unit="arquivo"):
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(zip_file, 'r') as z:
                z.extractall(tmpdir)
                arquivos_csv = glob.glob(os.path.join(tmpdir, '**/*.csv'), recursive=True)

                for csv_path in tqdm(arquivos_csv, desc=f"{os.path.basename(zip_file)}", leave=False, unit="csv"):
                    processar_csv(csv_path)

    print("\n✅ Importação finalizada!")
