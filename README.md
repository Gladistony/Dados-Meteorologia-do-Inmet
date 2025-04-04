# 🌤️ Processador de Dados Meteorológicos do INMET

Este projeto em Python lê e processa arquivos de dados meteorológicos históricos disponibilizados pelo [INMET (Instituto Nacional de Meteorologia)](https://portal.inmet.gov.br/dadoshistoricos), armazena as informações em um banco de dados SQLite e organiza os dados em tabelas relacionais utilizando SQLAlchemy.

---

## ⚙️ Requisitos

- Python **3.12**
- [pip](https://pip.pypa.io/en/stable/installation/)

### 📦 Instalar dependências

Use o comando abaixo para instalar todas as bibliotecas necessárias:

```bash
pip install sqlalchemy pandas tqdm
```

---

## 📁 Estrutura de Arquivos

```
.
├── Main.py                  # Script principal que processa os dados
├── clima.db                 # Banco de dados SQLite gerado automaticamente
├── dados/                   # Pasta onde você deve colocar os arquivos .zip do INMET
│   ├── 2000.zip
│   ├── 2001.zip
│   └── ...
└── README.md
```

---

## 📅 Onde obter os dados

1. Acesse o site do [INMET - Dados Históricos](https://portal.inmet.gov.br/dadoshistoricos).
2. Baixe os arquivos `.zip` desejados (um por ano).
3. Coloque todos os arquivos `.zip` dentro da pasta `./dados`.

⚠️ Os arquivos `.zip` devem conter os arquivos `.csv` no formato original fornecido pelo INMET.

---

## ▶️ Como executar

Execute o script principal com o Python:

```bash
python Main.py
```

Durante a execução, o script irá:

- Ler todos os arquivos `.zip` na pasta `./dados`
- Extrair os `.csv` de cada ano
- Processar os metadados da estação
- Armazenar os dados meteorológicos no banco SQLite (`clima_brasilia.db`)
- Mostrar uma barra de progresso para cada `.zip` e seus respectivos `.csv`

---

## 🧹 Tabelas no banco de dados

O script cria automaticamente duas tabelas:

### 🔹 estacao

| Campo           | Tipo       |
|----------------|------------|
| id             | Integer (PK) |
| regiao         | String     |
| uf             | String     |
| nome_estacao   | String     |
| codigo_wmo     | String     |
| latitude       | Decimal    |
| longitude      | Decimal    |
| altitude       | Decimal    |
| data_fundacao  | Date       |

### 🔸 dados_meteorologicos

| Campo                                       | Tipo       |
|--------------------------------------------|------------|
| id                                         | Integer (PK) |
| estacao_id                                 | ForeignKey -> estacao.id |
| data                                       | Date       |
| hora                                       | Time       |
| precipitacao_total_mm                      | Decimal    |
| pressao_nivel_estacao_mB                  | Decimal    |
| pressao_max_na_hora_ant_mB                | Decimal    |
| pressao_min_na_hora_ant_mB                | Decimal    |
| radiacao_global_KJ_m2                      | Decimal    |
| temperatura_bulbo_seco_C                  | Decimal    |
| temperatura_orvalho_C                     | Decimal    |
| temperatura_max_na_hora_ant_C             | Decimal    |
| temperatura_min_na_hora_ant_C             | Decimal    |
| temperatura_orvalho_max_hora_ant_C        | Decimal    |
| temperatura_orvalho_min_hora_ant_C        | Decimal    |
| umidade_relativa_max_hora_ant_percent     | Decimal    |
| umidade_relativa_min_hora_ant_percent     | Decimal    |
| umidade_relativa_percent                  | Decimal    |
| vento_direcao_graus                        | Decimal    |
| vento_rajada_max_m_s                      | Decimal    |
| vento_velocidade_m_s                      | Decimal    |

---

## 📌 Observações

- Dados ausentes são tratados como `NULL`
- Dados com valor `-9999` são ignorados automaticamente
- O sistema é tolerante a erros de leitura de linha ou CSV malformado

---

## 💬 Contribuição

Fique à vontade para contribuir com melhorias, correções ou novas funcionalidades via pull requests ou issues!

---

## 📄 Licença

Este projeto está sob a licença MIT.
