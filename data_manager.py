"""
Módulo de gerenciamento e geração de dados sintéticos para o Dashboard de BI.
Utiliza Pandas e DuckDB para modelagem e consultas analíticas de alta performance.
"""

from datetime import datetime, timedelta
from pathlib import Path
import os
import re
import numpy as np
import pandas as pd

# Suporte ao DuckDB com fallback resiliente para Pandas puro se duckdb não estiver instalado
try:
    import duckdb
    HAS_DUCKDB = True
except ImportError:
    duckdb = None
    HAS_DUCKDB = False

DATA_DIR = Path("data")

# Dicionário de produtos e faixas de preços por categoria
CATALOGO_PRODUTOS = {
    "Eletrônicos": [
        ("Smartphone 5G Pro", 3299.90, 0.35),
        ("Notebook Ultra Slim", 4599.00, 0.28),
        ("Smart TV 55\" 4K", 2899.00, 0.30),
        ("Fone de Ouvido Bluetooth ANC", 489.90, 0.42),
        ("Tablet 10.5\" Octa-core", 1799.00, 0.33),
        ("Smartwatch Fitness", 699.90, 0.40),
    ],
    "Moda & Acessórios": [
        ("Camiseta Básica Algodão Pima", 89.90, 0.55),
        ("Calça Jeans Premium Slim", 229.90, 0.48),
        ("Tênis Esportivo Running", 389.90, 0.45),
        ("Jaqueta Corta-Vento Térmica", 279.90, 0.50),
        ("Mochila Executiva Impermeável", 199.90, 0.52),
    ],
    "Casa & Decoração": [
        ("Cadeira Ergonômica Office", 890.00, 0.38),
        ("Luminária Inteligente LED", 169.90, 0.46),
        ("Jogo de Panelas Cerâmica (5 peças)", 499.90, 0.35),
        ("Aspirador de Pó Robô Smart", 1290.00, 0.30),
        ("Mesa Lateral Minimalista", 249.90, 0.40),
    ],
    "Beleza & Saúde": [
        ("Kit Skincare Anti-idade", 259.90, 0.58),
        ("Sérum Facial Vitamina C", 119.90, 0.62),
        ("Perfume Eau de Parfum 100ml", 349.90, 0.50),
        ("Protetor Solar Facial FPS 60", 79.90, 0.55),
        ("Massageador Elétrico Portátil", 189.90, 0.45),
    ],
    "Alimentos & Gourmet": [
        ("Café Especial em Grãos 1kg", 84.90, 0.40),
        ("Azeite de Oliva Extra Virgem 500ml", 69.90, 0.35),
        ("Vinho Tinto Reserva Importado", 139.90, 0.42),
        ("Caixa de Chocolates Artesanais", 59.90, 0.48),
        ("Kit Queijos Artesanais da Canastra", 119.90, 0.38),
    ],
}

REGIOES = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
PESOS_REGIOES = [0.44, 0.22, 0.18, 0.10, 0.06]

CANAIS = ["E-commerce", "Loja Física", "Marketplace"]
PESOS_CANAIS = [0.50, 0.30, 0.20]

PAGAMENTOS = ["Pix", "Cartão de Crédito", "Boleto Bancário", "Cartão de Débito"]
PESOS_PAGAMENTOS = [0.45, 0.38, 0.12, 0.05]

STATUS_PEDIDO = ["Concluído", "Cancelado", "Devolvido"]
PESOS_STATUS = [0.90, 0.06, 0.04]


def generate_sales_data(num_records: int = 4000, days_back: int = 180, seed: int = 42) -> pd.DataFrame:
    """
    Gera um DataFrame sintético com histórico detalhado de vendas.
    """
    np.random.seed(seed)
    hoje = datetime.now().date()
    data_inicial = hoje - timedelta(days=days_back)

    # Lista achatada de produtos para amostragem
    todos_produtos = []
    for cat, prods in CATALOGO_PRODUTOS.items():
        for nome, preco, margem in prods:
            todos_produtos.append((cat, nome, preco, margem))

    indices_produtos = np.random.choice(len(todos_produtos), size=num_records)
    
    # Gera datas aleatórias com leve tendência de crescimento ao longo do tempo
    pesos_temporais = np.linspace(1.0, 1.8, days_back)
    pesos_temporais /= pesos_temporais.sum()
    dias_offset = np.random.choice(range(days_back), size=num_records, p=pesos_temporais)

    registros = []
    for i in range(num_records):
        cat, nome_prod, preco_base, margem_padrao = todos_produtos[indices_produtos[i]]
        
        # Variação de preço unitário (+/- 5%)
        variacao_preco = np.random.uniform(0.95, 1.05)
        preco_unitario = round(preco_base * variacao_preco, 2)

        # Quantidade comprada (1 a 4 unidades)
        quantidade = int(np.random.choice([1, 2, 3, 4], p=[0.65, 0.22, 0.09, 0.04]))
        faturamento = round(preco_unitario * quantidade, 2)

        # Margem de lucro com leve ruído
        margem = np.clip(margem_padrao + np.random.uniform(-0.04, 0.04), 0.15, 0.70)
        lucro = round(faturamento * margem, 2)
        custo = round(faturamento - lucro, 2)

        data_pedido = data_inicial + timedelta(days=int(dias_offset[i]))
        regiao = np.random.choice(REGIOES, p=PESOS_REGIOES)
        canal = np.random.choice(CANAIS, p=PESOS_CANAIS)
        pagamento = np.random.choice(PAGAMENTOS, p=PESOS_PAGAMENTOS)
        status = np.random.choice(STATUS_PEDIDO, p=PESOS_STATUS)

        registros.append({
            "id_pedido": f"PED-{100000 + i}",
            "data": pd.to_datetime(data_pedido),
            "categoria": cat,
            "produto": nome_prod,
            "regiao": regiao,
            "canal": canal,
            "quantidade": quantidade,
            "preco_unitario": preco_unitario,
            "faturamento": faturamento,
            "custo": custo,
            "lucro": lucro,
            "margem_percentual": round(margem * 100, 1),
            "forma_pagamento": pagamento,
            "status": status,
        })

    df = pd.DataFrame(registros)
    df = df.sort_values(by="data").reset_index(drop=True)
    return df


def filter_sales_data(
    df: pd.DataFrame,
    start_date=None,
    end_date=None,
    categories: list = None,
    regions: list = None,
    channels: list = None,
    only_completed: bool = True,
) -> pd.DataFrame:
    """
    Aplica filtros no conjunto de dados de vendas.
    """
    df_filtered = df.copy()

    if start_date:
        df_filtered = df_filtered[df_filtered["data"].dt.date >= start_date]

    if end_date:
        df_filtered = df_filtered[df_filtered["data"].dt.date <= end_date]

    if categories:
        df_filtered = df_filtered[df_filtered["categoria"].isin(categories)]

    if regions:
        df_filtered = df_filtered[df_filtered["regiao"].isin(regions)]

    if channels:
        df_filtered = df_filtered[df_filtered["canal"].isin(channels)]

    if only_completed:
        df_filtered = df_filtered[df_filtered["status"] == "Concluído"]

    return df_filtered


def run_duckdb_query(sql_query: str, df: pd.DataFrame) -> pd.DataFrame:
    """
    Executa uma consulta SQL usando DuckDB diretamente sobre o DataFrame 'df'.
    Se DuckDB não estiver instalado no ambiente, utiliza Pandas como fallback.
    """
    if HAS_DUCKDB:
        try:
            con = duckdb.connect(database=":memory:")
            con.register("vendas", df)
            con.register("df", df)
            result_df = con.execute(sql_query).df()
            con.close()
            return result_df
        except Exception as e:
            raise RuntimeError(f"Erro ao executar consulta DuckDB: {str(e)}")
    else:
        # Fallback simplificado quando executado localmente sem DuckDB instalado
        return df


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calcula os KPIs analíticos essenciais utilizando DuckDB (ou Pandas em caso de fallback).
    """
    if df.empty:
        return {
            "faturamento_total": 0.0,
            "total_pedidos": 0,
            "ticket_medio": 0.0,
            "lucro_total": 0.0,
            "margem_media": 0.0,
            "total_itens": 0,
        }

    if HAS_DUCKDB:
        query = """
            SELECT 
                COALESCE(SUM(faturamento), 0) AS faturamento_total,
                COUNT(DISTINCT id_pedido) AS total_pedidos,
                COALESCE(SUM(faturamento) / NULLIF(COUNT(DISTINCT id_pedido), 0), 0) AS ticket_medio,
                COALESCE(SUM(lucro), 0) AS lucro_total,
                COALESCE((SUM(lucro) / NULLIF(SUM(faturamento), 0)) * 100, 0) AS margem_media,
                COALESCE(SUM(quantidade), 0) AS total_itens
            FROM df
        """
        res = run_duckdb_query(query, df).iloc[0]
        return {
            "faturamento_total": float(res["faturamento_total"]),
            "total_pedidos": int(res["total_pedidos"]),
            "ticket_medio": float(res["ticket_medio"]),
            "lucro_total": float(res["lucro_total"]),
            "margem_media": float(res["margem_media"]),
            "total_itens": int(res["total_itens"]),
        }
    else:
        # Cálculo vetorizado com Pandas puro
        faturamento_total = float(df["faturamento"].sum())
        total_pedidos = int(df["id_pedido"].nunique())
        ticket_medio = faturamento_total / total_pedidos if total_pedidos > 0 else 0.0
        lucro_total = float(df["lucro"].sum())
        margem_media = (lucro_total / faturamento_total * 100) if faturamento_total > 0 else 0.0
        total_itens = int(df["quantidade"].sum())
        return {
            "faturamento_total": faturamento_total,
            "total_pedidos": total_pedidos,
            "ticket_medio": ticket_medio,
            "lucro_total": lucro_total,
            "margem_media": margem_media,
            "total_itens": total_itens,
        }


# =============================================================
# SUPORTE A BASES DE DADOS LOCAIS (KAGGLE / ARQUIVOS EM data/)
# =============================================================
def list_local_data_files(directory: Path = DATA_DIR) -> list:
    """
    Lista arquivos compatíveis (.csv, .xlsx, .xls, .parquet) na pasta de dados.
    """
    if not directory.exists():
        return []
    
    extensoes_validas = {".csv", ".xlsx", ".xls", ".parquet"}
    arquivos = []
    for item in directory.glob("*"):
        if item.is_file() and item.suffix.lower() in extensoes_validas:
            tamanho_kb = item.stat().st_size / 1024
            arquivos.append({
                "nome": item.name,
                "caminho": str(item),
                "extensao": item.suffix.lower(),
                "tamanho_kb": round(tamanho_kb, 1),
            })
    return sorted(arquivos, key=lambda x: x["nome"])


def load_single_file(file_path: str) -> dict:
    """
    Carrega um arquivo CSV, Parquet ou Excel.
    Se for Excel com múltiplas abas, retorna um dicionário com cada aba.
    """
    p = Path(file_path)
    ext = p.suffix.lower()
    tabelas = {}

    nome_base = re.sub(r'[^a-zA-Z0-9_]', '_', p.stem).lower()

    if ext == ".csv":
        try:
            # Tenta ler com separador vírgula e encoding utf-8
            df = pd.read_csv(p, encoding="utf-8")
        except Exception:
            try:
                # Tenta ler com separador ponto e vírgula e latin1
                df = pd.read_csv(p, sep=";", encoding="latin1")
            except Exception as e:
                df = pd.read_csv(p, sep=None, engine="python")
        tabelas[nome_base] = df

    elif ext in [".xlsx", ".xls"]:
        xls = pd.ExcelFile(p)
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name)
            sheet_slug = re.sub(r'[^a-zA-Z0-9_]', '_', sheet_name).lower()
            chave = f"{nome_base}_{sheet_slug}" if len(xls.sheet_names) > 1 else nome_base
            tabelas[chave] = df

    elif ext == ".parquet":
        df = pd.read_parquet(p)
        tabelas[nome_base] = df

    return tabelas


def load_all_local_tables(directory: Path = DATA_DIR) -> dict:
    """
    Carrega todas as tabelas e planilhas encontradas na pasta data/.
    Retorna um dicionário: {"nome_tabela": pd.DataFrame}
    """
    arquivos = list_local_data_files(directory)
    todas_tabelas = {}
    for arq in arquivos:
        try:
            tabs = load_single_file(arq["caminho"])
            todas_tabelas.update(tabs)
        except Exception as e:
            print(f"Erro ao carregar {arq['nome']}: {e}")
    return todas_tabelas


def execute_duckdb_multi_table(sql_query: str, tables: dict) -> pd.DataFrame:
    """
    Executa consulta SQL via DuckDB podendo fazer JOINs entre qualquer uma das tabelas carregadas!
    """
    if not HAS_DUCKDB:
        raise RuntimeError("DuckDB não está disponível no ambiente atual.")
    
    con = duckdb.connect(database=":memory:")
    for nome_tab, df_tab in tables.items():
        con.register(nome_tab, df_tab)

    result_df = con.execute(sql_query).df()
    con.close()
    return result_df

