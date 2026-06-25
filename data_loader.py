"""
data_loader.py — Carga, transformação e cálculos econômicos dos dados do Comex Stat.

Carrega dados reais dos arquivos Excel do MDIC e transforma para formato long,
calculando agregados, índices e rankings para o dashboard.
"""

import os
import numpy as np
import pandas as pd
import streamlit as st

from config import (
    ARQUIVO_UF,
    ARQUIVO_SECAO,
    ARQUIVO_HISTORICO,
    ANO_BASE_INDICE,
    PERIODO_PASSADO,
    PERIODO_PRESENTE,
)

# ═══════════════════════════════════════════════════════════════════════════════
# DIRETÓRIO BASE (onde estão os .xlsx)
# ═══════════════════════════════════════════════════════════════════════════════
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES DE CARGA — FORMATO WIDE → LONG
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def load_uf_data() -> pd.DataFrame:
    """
    Carrega o arquivo de Exportação/Importação por UF (1997–2026).
    Retorna DataFrame long: [Ano, UF, Exportacao, Importacao]
    """
    path = os.path.join(BASE_DIR, ARQUIVO_UF)
    df = pd.read_excel(path)

    # Identificar colunas de valores (padrão: "Exportação - YYYY - Valor US$ FOB")
    exp_cols = [c for c in df.columns if "Exporta" in c and "Valor" in c]
    imp_cols = [c for c in df.columns if "Importa" in c and "Valor" in c]

    # Extrair anos das colunas
    records = []
    for _, row in df.iterrows():
        uf = str(row.iloc[1]).strip()
        if uf in ("", "nan", "None"):
            continue
        for ec, ic in zip(sorted(exp_cols), sorted(imp_cols)):
            # Extrair ano do nome da coluna (ex: "Exportação - 2024 - Valor US$ FOB")
            ano = int("".join(filter(str.isdigit, ec.split("-")[1].strip())))
            exp_val = pd.to_numeric(row[ec], errors="coerce")
            imp_val = pd.to_numeric(row[ic], errors="coerce")
            records.append({
                "Ano": ano,
                "UF": uf,
                "Exportacao": exp_val if pd.notna(exp_val) else 0,
                "Importacao": imp_val if pd.notna(imp_val) else 0,
            })

    result = pd.DataFrame(records)
    # Filtrar UFs especiais (Exterior, Reexportação, etc.)
    ufs_excluir = [
        "Exterior", "Reexportação", "Mercadoria Nacionalizada",
        "Consumo de Bordo", "Zona Não Declarada", "Não Declarada",
    ]
    result = result[~result["UF"].isin(ufs_excluir)]
    return result.sort_values(["Ano", "UF"]).reset_index(drop=True)


@st.cache_data(ttl=3600)
def load_secao_data() -> pd.DataFrame:
    """
    Carrega o arquivo de Exportação/Importação por Via + Seção NCM (1997–2026).
    Retorna DataFrame long: [Ano, Via, CodigoSecao, DescricaoSecao, Exportacao, Importacao]
    """
    path = os.path.join(BASE_DIR, ARQUIVO_SECAO)
    df = pd.read_excel(path)

    exp_cols = [c for c in df.columns if "Exporta" in c and "Valor" in c]
    imp_cols = [c for c in df.columns if "Importa" in c and "Valor" in c]

    records = []
    for _, row in df.iterrows():
        via = str(row.iloc[1]).strip()
        cod_secao = str(row.iloc[2]).strip()
        desc_secao = str(row.iloc[3]).strip()
        for ec, ic in zip(sorted(exp_cols), sorted(imp_cols)):
            ano = int("".join(filter(str.isdigit, ec.split("-")[1].strip())))
            exp_val = pd.to_numeric(row[ec], errors="coerce")
            imp_val = pd.to_numeric(row[ic], errors="coerce")
            records.append({
                "Ano": ano,
                "Via": via,
                "CodigoSecao": cod_secao,
                "DescricaoSecao": desc_secao,
                "Exportacao": exp_val if pd.notna(exp_val) else 0,
                "Importacao": imp_val if pd.notna(imp_val) else 0,
            })

    return pd.DataFrame(records).sort_values(["Ano", "CodigoSecao"]).reset_index(drop=True)


@st.cache_data(ttl=3600)
def load_historical_data() -> pd.DataFrame:
    """
    Carrega o arquivo de dados históricos por Produto NBM (1989–1996).
    Retorna DataFrame long: [Ano, UF, CodigoNBM, DescricaoNBM, Exportacao, Importacao]
    """
    path = os.path.join(BASE_DIR, ARQUIVO_HISTORICO)
    df = pd.read_excel(path)

    exp_cols = [c for c in df.columns if "Exporta" in c and "Valor" in c]
    imp_cols = [c for c in df.columns if "Importa" in c and "Valor" in c]

    records = []
    for _, row in df.iterrows():
        uf = str(row.iloc[1]).strip().replace("\n", "")
        cod_nbm = row.iloc[2]
        desc_nbm = str(row.iloc[3]).strip().replace("\n", "")
        for ec, ic in zip(sorted(exp_cols), sorted(imp_cols)):
            ano = int("".join(filter(str.isdigit, ec.split("-")[1].strip())))
            exp_val = pd.to_numeric(row[ec], errors="coerce")
            imp_val = pd.to_numeric(row[ic], errors="coerce")
            records.append({
                "Ano": ano,
                "UF": uf,
                "CodigoNBM": cod_nbm,
                "DescricaoNBM": desc_nbm,
                "Exportacao": exp_val if pd.notna(exp_val) else 0,
                "Importacao": imp_val if pd.notna(imp_val) else 0,
            })

    return pd.DataFrame(records).sort_values(["Ano"]).reset_index(drop=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CÁLCULOS ECONÔMICOS — AGREGADOS ANUAIS
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def compute_aggregates(df_uf: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula totais anuais agregados:
      - Exportacao: soma anual de todas as UFs
      - Importacao: soma anual de todas as UFs
      - SaldoComercial = Exportacao - Importacao
      - CorrenteComercio = Exportacao + Importacao
    """
    agg = df_uf.groupby("Ano").agg(
        Exportacao=("Exportacao", "sum"),
        Importacao=("Importacao", "sum"),
    ).reset_index()

    # Fórmulas econômicas
    agg["SaldoComercial"] = agg["Exportacao"] - agg["Importacao"]
    agg["CorrenteComercio"] = agg["Exportacao"] + agg["Importacao"]

    return agg.sort_values("Ano").reset_index(drop=True)


@st.cache_data(ttl=3600)
def compute_secao_aggregates(df_secao: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega dados de seção por ano (somando todas as vias).
    Retorna: [Ano, CodigoSecao, DescricaoSecao, Exportacao, Importacao]
    """
    agg = df_secao.groupby(["Ano", "CodigoSecao", "DescricaoSecao"]).agg(
        Exportacao=("Exportacao", "sum"),
        Importacao=("Importacao", "sum"),
    ).reset_index()
    return agg.sort_values(["Ano", "CodigoSecao"]).reset_index(drop=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CÁLCULOS ECONÔMICOS — ÍNDICE BASE 100
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def compute_index_base100(agg: pd.DataFrame, ano_base: int = ANO_BASE_INDICE) -> pd.DataFrame:
    """
    Calcula índice base 100 para Exportação, Importação e Corrente de Comércio.
    Fórmula: Índice = (Valor do ano atual / Valor do ano base) × 100
    """
    row_base = agg[agg["Ano"] == ano_base]
    if row_base.empty:
        return agg  # Retorna sem índice se ano base não disponível

    base_exp = row_base["Exportacao"].values[0]
    base_imp = row_base["Importacao"].values[0]
    base_corr = row_base["CorrenteComercio"].values[0]

    idx = agg.copy()
    idx["IndiceExportacao"] = (idx["Exportacao"] / base_exp) * 100 if base_exp > 0 else 100
    idx["IndiceImportacao"] = (idx["Importacao"] / base_imp) * 100 if base_imp > 0 else 100
    idx["IndiceCorrente"] = (idx["CorrenteComercio"] / base_corr) * 100 if base_corr > 0 else 100

    return idx


# ═══════════════════════════════════════════════════════════════════════════════
# CÁLCULOS ECONÔMICOS — TAXA DE CRESCIMENTO
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def compute_growth_rates(agg: pd.DataFrame) -> pd.DataFrame:
    """
    Calcula taxa de crescimento anual (%) para Exportação, Importação e Corrente.
    Fórmula: Taxa(%) = ((Valor_t / Valor_{t-1}) - 1) × 100
    """
    gr = agg.sort_values("Ano").copy()
    gr["CrescimentoExportacao"] = gr["Exportacao"].pct_change() * 100
    gr["CrescimentoImportacao"] = gr["Importacao"].pct_change() * 100
    gr["CrescimentoCorrente"] = gr["CorrenteComercio"].pct_change() * 100
    return gr


# ═══════════════════════════════════════════════════════════════════════════════
# RANKINGS E TOP PRODUTOS
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def get_top_secoes(
    df_secao_agg: pd.DataFrame,
    periodo: tuple[int, int],
    tipo: str = "Exportacao",
    top_n: int = 10,
) -> pd.DataFrame:
    """
    Retorna top N seções NCM por valor acumulado no período.
    tipo: 'Exportacao' ou 'Importacao'
    """
    mask = (df_secao_agg["Ano"] >= periodo[0]) & (df_secao_agg["Ano"] <= periodo[1])
    subset = df_secao_agg[mask].copy()

    ranking = (
        subset.groupby(["CodigoSecao", "DescricaoSecao"])[tipo]
        .sum()
        .reset_index()
        .sort_values(tipo, ascending=False)
        .head(top_n)
    )
    return ranking


@st.cache_data(ttl=3600)
def get_uf_ranking(
    df_uf: pd.DataFrame,
    periodo: tuple[int, int],
    tipo: str = "Exportacao",
    top_n: int = 15,
) -> pd.DataFrame:
    """
    Retorna ranking das UFs por valor acumulado no período.
    """
    mask = (df_uf["Ano"] >= periodo[0]) & (df_uf["Ano"] <= periodo[1])
    subset = df_uf[mask].copy()

    ranking = (
        subset.groupby("UF")[tipo]
        .sum()
        .reset_index()
        .sort_values(tipo, ascending=False)
        .head(top_n)
    )
    return ranking


@st.cache_data(ttl=3600)
def get_top_secoes_evolucao(
    df_secao_agg: pd.DataFrame,
    periodo: tuple[int, int],
    tipo: str = "Exportacao",
    top_n: int = 3,
) -> pd.DataFrame:
    """
    Retorna a evolução temporal do top N seções no período.
    """
    # Identificar top N seções pelo valor acumulado
    top = get_top_secoes(df_secao_agg, periodo, tipo, top_n)
    top_codigos = top["CodigoSecao"].tolist()

    mask = (
        (df_secao_agg["Ano"] >= periodo[0])
        & (df_secao_agg["Ano"] <= periodo[1])
        & (df_secao_agg["CodigoSecao"].isin(top_codigos))
    )
    return df_secao_agg[mask].copy()


# ═══════════════════════════════════════════════════════════════════════════════
# PROJEÇÕES — CENÁRIOS 2026–2030
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def compute_projections(agg: pd.DataFrame) -> pd.DataFrame:
    """
    Gera projeções 2026–2030 com três cenários econômicos.

    Cenário Conservador: crescimento baixo/negativo (EU desacelerando, barreiras)
    Cenário Base: manutenção da tendência recente
    Cenário Otimista: demanda acelerada por commodities, diversificação

    Usa o valor real de 2025 como base para projetar.
    """
    # Obter valor real de 2025 como ponto de partida
    row_2025 = agg[agg["Ano"] == 2025]
    if row_2025.empty:
        # Fallback: usar o último ano disponível
        row_2025 = agg.iloc[[-1]]

    exp_base = row_2025["Exportacao"].values[0]
    imp_base = row_2025["Importacao"].values[0]

    # Taxas de crescimento anual por cenário
    taxas = {
        "Conservador": {
            "exp": [-0.02, -0.01, 0.00, 0.01, 0.01],
            "imp": [0.01, 0.00, -0.01, 0.00, 0.01],
        },
        "Base": {
            "exp": [0.03, 0.035, 0.04, 0.04, 0.045],
            "imp": [0.025, 0.03, 0.03, 0.035, 0.035],
        },
        "Otimista": {
            "exp": [0.07, 0.08, 0.09, 0.10, 0.10],
            "imp": [0.05, 0.06, 0.06, 0.07, 0.07],
        },
    }

    records = []
    for cenario, rates in taxas.items():
        e = exp_base
        i = imp_base
        for idx, ano in enumerate(range(2026, 2031)):
            e = e * (1 + rates["exp"][idx])
            i = i * (1 + rates["imp"][idx])
            records.append({
                "Ano": ano,
                "Cenario": cenario,
                "Exportacao": e,
                "Importacao": i,
                "SaldoComercial": e - i,
                "CorrenteComercio": e + i,
            })

    return pd.DataFrame(records)


# ═══════════════════════════════════════════════════════════════════════════════
# FILTROS DE PERÍODO
# ═══════════════════════════════════════════════════════════════════════════════

def filter_period(df: pd.DataFrame, periodo: tuple[int, int]) -> pd.DataFrame:
    """Filtra DataFrame por período [inicio, fim] (inclusive)."""
    return df[(df["Ano"] >= periodo[0]) & (df["Ano"] <= periodo[1])].copy()
