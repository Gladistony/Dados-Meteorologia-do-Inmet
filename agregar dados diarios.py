import os
from tqdm import tqdm
from sqlalchemy import create_engine, Column, Integer, String, Date, Time, DECIMAL, ForeignKey, func
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Configurações
ARQUIVO_DB = 'clima.db'

# SQLAlchemy setup
Base = declarative_base()
engine = create_engine(f'sqlite:///{ARQUIVO_DB}')
Session = sessionmaker(bind=engine)
session = Session()

# Modelos existentes
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

# Nova tabela de agregação diária
class DadoMeteorologicoDiario(Base):
    __tablename__ = 'dados_meteorologicos_diarios'
    id = Column(Integer, primary_key=True)
    estacao_id = Column(Integer, ForeignKey('estacao.id'))
    data = Column(Date)
    precipitacao_total_mm = Column(DECIMAL(10, 2))
    pressao_nivel_estacao_mB = Column(DECIMAL(10, 2))
    pressao_max_ant_mB = Column(DECIMAL(10, 2))
    pressao_min_ant_mB = Column(DECIMAL(10, 2))
    radiacao_global_KJ_m2 = Column(DECIMAL(10, 2))  # SOMA em vez de média
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

# Criar a tabela se ainda não existir
Base.metadata.create_all(engine)

# Consulta com agregações
query = session.query(
    DadoMeteorologico.estacao_id,
    DadoMeteorologico.data,
    func.avg(DadoMeteorologico.precipitacao_total_mm),
    func.avg(DadoMeteorologico.pressao_nivel_estacao_mB),
    func.avg(DadoMeteorologico.pressao_max_ant_mB),
    func.avg(DadoMeteorologico.pressao_min_ant_mB),
    func.sum(DadoMeteorologico.radiacao_global_KJ_m2),  # ← SOMA aqui!
    func.avg(DadoMeteorologico.temp_bulbo_seco_C),
    func.avg(DadoMeteorologico.temp_ponto_orvalho_C),
    func.avg(DadoMeteorologico.temp_max_ant_C),
    func.avg(DadoMeteorologico.temp_min_ant_C),
    func.avg(DadoMeteorologico.temp_orvalho_max_ant_C),
    func.avg(DadoMeteorologico.temp_orvalho_min_ant_C),
    func.avg(DadoMeteorologico.umidade_rel_max_ant_pct),
    func.avg(DadoMeteorologico.umidade_rel_min_ant_pct),
    func.avg(DadoMeteorologico.umidade_rel_ar_pct),
    func.avg(DadoMeteorologico.vento_direcao_graus),
    func.avg(DadoMeteorologico.vento_rajada_max_ms),
    func.avg(DadoMeteorologico.vento_velocidade_ms)
).group_by(DadoMeteorologico.estacao_id, DadoMeteorologico.data)

# Executa a query e insere com barra de progresso
resultados = query.all()
print(f"Inserindo {len(resultados)} registros diários agregados...\n")

for row in tqdm(resultados, desc="Inserindo dados agregados", unit="registro"):
    dado_diario = DadoMeteorologicoDiario(
        estacao_id=row[0],
        data=row[1],
        precipitacao_total_mm=row[2],
        pressao_nivel_estacao_mB=row[3],
        pressao_max_ant_mB=row[4],
        pressao_min_ant_mB=row[5],
        radiacao_global_KJ_m2=row[6],
        temp_bulbo_seco_C=row[7],
        temp_ponto_orvalho_C=row[8],
        temp_max_ant_C=row[9],
        temp_min_ant_C=row[10],
        temp_orvalho_max_ant_C=row[11],
        temp_orvalho_min_ant_C=row[12],
        umidade_rel_max_ant_pct=row[13],
        umidade_rel_min_ant_pct=row[14],
        umidade_rel_ar_pct=row[15],
        vento_direcao_graus=row[16],
        vento_rajada_max_ms=row[17],
        vento_velocidade_ms=row[18]
    )
    session.add(dado_diario)

session.commit()
session.close()

print("\n✅ Dados diários agregados inseridos com sucesso!")
