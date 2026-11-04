"""
Produção de Petróleo, Líquidos de Gás Natural (LGN) e Gás Natural

Autor: Antonino Marques Jares
Fonte: Dados Abertos do GovBR

Script convertido do notebook producao_petroleo_gas_lgn.ipynb
com persistência em SQLite (producao.db), consulta SQL ordenada,
exportação final para JSON (pasta etl/) com envelope de metadados,
exclusão de registros com PRODUCAO nula e remoção do banco ao final.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd


# Dicionário de mapeamento (abreviação → número com dois dígitos)
mes_para_numero = {
    'JAN': '01', 'FEV': '02', 'MAR': '03', 'ABR': '04', 'MAI': '05', 'JUN': '06',
    'JUL': '07', 'AGO': '08', 'SET': '09', 'OUT': '10', 'NOV': '11', 'DEZ': '12'
}


# =============================================================================
# 1 - DF de Produção de Líquido de Gás Natural (LGN) em Metros Cúbicos
# =============================================================================
CSV_LGN = Path(r"D:\ETL\nivel_01_bronze\producao\producao-lgn-m3.csv")

df_lgn = pd.read_csv(CSV_LGN, sep=';', encoding='utf-8', low_memory=False)

df_lgn['PAIS'] = 'BRASIL'

df_lgn = df_lgn.rename(columns={
    'MÊS': 'MES',
    'GRANDE REGIÃO': 'REGIAO',
    'UNIDADE DA FEDERAÇÃO': 'UF',
    'LOCALIZAÇÃO': 'LOCAL',
    'PRODUÇÃO': 'PRODUCAO_M3',
})

df_lgn['MES'] = df_lgn['MES'].str.upper().map(mes_para_numero)

# Cria MES_ANO
df_lgn['MES_ANO'] = df_lgn['MES'] + '/' + df_lgn['ANO'].astype(str)

df_lgn = df_lgn[['PAIS', 'MES_ANO', 'PRODUTO', 'PRODUCAO_M3']]

print("=== DF LGN ===")
print(df_lgn.dtypes)
print(df_lgn.head())
print()


# =============================================================================
# 2 - DF de Produção de Petróleo em Metros Cúbicos
# =============================================================================
CSV_PETROLEO = Path(r"D:\ETL\nivel_01_bronze\producao\producao-petroleo-m3.csv")

df_petroleo = pd.read_csv(CSV_PETROLEO, sep=';', encoding='utf-8', low_memory=False)

df_petroleo['PAIS'] = 'BRASIL'

df_petroleo = df_petroleo.rename(columns={
    'MÊS': 'MES',
    'GRANDE REGIÃO': 'REGIAO',
    'UNIDADE DA FEDERAÇÃO': 'UF',
    'LOCALIZAÇÃO': 'LOCAL',
    'PRODUÇÃO': 'PRODUCAO_M3',
})

df_petroleo['MES'] = df_petroleo['MES'].str.upper().map(mes_para_numero)

# Cria MES_ANO
df_petroleo['MES_ANO'] = df_petroleo['MES'] + '/' + df_petroleo['ANO'].astype(str)

df_petroleo = df_petroleo[['PAIS', 'MES_ANO', 'PRODUTO', 'PRODUCAO_M3']]

print("=== DF PETRÓLEO ===")
print(df_petroleo.head())
print()


# =============================================================================
# 3 - DF de Produção de Gás Natural em Metros Cúbicos
# Como os outros datasets estão em metros cúbicos precisamos ter a mesma medida
# no gráfico (m3)
# =============================================================================
CSV_GAS_NATURAL = Path(r"D:\ETL\nivel_01_bronze\producao\producao-gas-natural-1000m3.csv")

df_gas_natural = pd.read_csv(CSV_GAS_NATURAL, sep=';', encoding='utf-8', low_memory=False)

df_gas_natural['PAIS'] = 'BRASIL'

df_gas_natural = df_gas_natural.rename(columns={
    'MÊS': 'MES',
    'GRANDE REGIÃO': 'REGIAO',
    'UNIDADE DA FEDERAÇÃO': 'UF',
    'LOCALIZAÇÃO': 'LOCAL',
    'PRODUÇÃO': 'PRODUCAO_M3',
})

df_gas_natural['MES'] = df_gas_natural['MES'].str.upper().map(mes_para_numero)

# Cria MES_ANO
df_gas_natural['MES_ANO'] = df_gas_natural['MES'] + '/' + df_gas_natural['ANO'].astype(str)

df_gas_natural['PRODUCAO_M3'] = df_gas_natural['PRODUCAO_M3']

df_gas_natural = df_gas_natural[['PAIS', 'MES_ANO', 'PRODUTO', 'PRODUCAO_M3']]

# Converte de string para numérico
df_gas_natural['PRODUCAO_M3'] = pd.to_numeric(df_gas_natural['PRODUCAO_M3'], errors='coerce')

#Onde PRODUCAO_M3 é NaN, substituímos por 0, pois não há produção registrada.
df_gas_natural['PRODUCAO_M3'] = df_gas_natural['PRODUCAO_M3'].fillna(0)

# Gás Natural está inicialmente em 1000 m³, mas para manter consistência com os outros datasets, vamos multiplicar por 1000 para ter em m³.
df_gas_natural['PRODUCAO_M3'] = df_gas_natural['PRODUCAO_M3'] * 1000

print("=== DF GÁS NATURAL ===")
print(df_gas_natural.head())
print()


# =============================================================================
# 4 - Persistência em SQLite (producao.db no diretório do projeto)
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "producao.db"
print(f"Banco de dados será salvo em: {DB_PATH}")

conn = sqlite3.connect(DB_PATH)
df_consulta = None

try:
    # Salva cada DataFrame em uma tabela específica
    df_lgn.to_sql("lgn", conn, if_exists="replace", index=False)
    df_petroleo.to_sql("petroleo", conn, if_exists="replace", index=False)
    df_gas_natural.to_sql("gas_natural", conn, if_exists="replace", index=False)

    # Cria uma view unificada com os três datasets
    conn.execute("DROP VIEW IF EXISTS producao;")
    conn.execute("""
        CREATE VIEW producao AS
            SELECT PAIS, MES_ANO, PRODUTO, PRODUCAO_M3 FROM lgn
            UNION ALL
            SELECT PAIS, MES_ANO, PRODUTO, PRODUCAO_M3 FROM petroleo
            UNION ALL
            SELECT PAIS, MES_ANO, PRODUTO, PRODUCAO_M3 FROM gas_natural;
    """)
    conn.commit()

    print("\nTabelas criadas: lgn, petroleo, gas_natural")
    print("View criada: producao (UNION ALL das três tabelas)")

    # -------------------------------------------------------------------------
    # 5 - Consulta SQL ordenada por PAIS, MES_ANO e PRODUTO
    # -------------------------------------------------------------------------
    # Como MES_ANO está no formato 'MM/AAAA', para ordenar cronologicamente
    # corretamente usamos substr para extrair ano e mês.
    query = """
        SELECT PAIS, MES_ANO, PRODUTO, PRODUCAO_M3 AS PRODUCAO
        FROM producao
        ORDER BY
            PAIS,
            substr(MES_ANO, 4, 4) ASC,  -- ano
            substr(MES_ANO, 1, 2) ASC,  -- mês
            PRODUTO;
    """

    df_consulta = pd.read_sql_query(query, conn)

    print("\n=== CONSULTA SQL (ordenada por PAIS, MES_ANO, PRODUTO) ===")
    print(f"Total de registros: {len(df_consulta)}")
    print(df_consulta.head(20).to_string(index=False))

finally:
    conn.close()
    print(f"\nConexão com {DB_PATH} encerrada.")


# =============================================================================
# 6 - Exporta df_consulta para JSON (pasta etl/) e remove o banco SQLite
# =============================================================================
ETL_DIR = BASE_DIR / "etl"
ETL_DIR.mkdir(parents=True, exist_ok=True)

JSON_PATH = ETL_DIR / "producao_petroleo_gas_e_lgn.json"

if df_consulta is not None:
    # -------------------------------------------------------------------------
    # Remove registros com PRODUCAO nula (NaN/None) para evitar JSON inválido
    # (o json.dump serializa NaN como o literal "NaN", que não é JSON válido)
    # -------------------------------------------------------------------------
    total_antes = len(df_consulta)
    df_export = df_consulta.dropna(subset=["PRODUCAO"]).copy()
    total_depois = len(df_export)
    removidos = total_antes - total_depois

    print(f"\nRegistros com PRODUCAO nula removidos: {removidos}")
    print(f"Registros válidos para exportação: {total_depois}")

    # Converte para lista de dicionários
    registros = df_export.to_dict(orient="records")

    # Envelope com metadados + dados
    payload = {
        "metadados": {
            "data_de_atualizacao": datetime.now().strftime("%d-%m-%Y"),
            "responsavel": "Antonino Marques Jares",
            "nome_programa": "etl_producao_petroleo_gas_e_lgn.py",
            "unidade_medida": "m³",
        },
        "dados": registros,
    }

    with JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump(
            payload,
            f,
            ensure_ascii=False,     # preserva acentos (ex.: "PETRÓLEO")
            indent=2,               # legível
            default=str,            # fallback para tipos não nativos
            allow_nan=False,        # rede de segurança: falha se ainda houver NaN
        )

    print(f"\nJSON exportado: {JSON_PATH}")
    print(f"Total de registros no JSON: {len(registros)}")
    print(f"Data de atualização: {payload['metadados']['data_de_atualizacao']}")
else:
    print("\nAVISO: df_consulta vazio — JSON não foi gerado.")


# Remove o banco SQLite após a exportação
if DB_PATH.exists():
    DB_PATH.unlink()
    print(f"Banco SQLite removido: {DB_PATH}")
else:
    print(f"Banco SQLite não encontrado em {DB_PATH} (nada a remover).")