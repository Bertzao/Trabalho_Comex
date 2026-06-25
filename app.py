"""
app.py — Dashboard Interativo: Relação Comercial Brasil–Países Baixos

Aplicação Streamlit com 5 abas para análise completa da relação comercial
bilateral, utilizando dados oficiais do Comex Stat (MDIC) e gráficos Plotly.

Execução:
    streamlit run app.py
"""

import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from config import (
    CUSTOM_CSS, ABAS, NAVY, NAVY_LIGHT, ORANGE, ORANGE_LIGHT,
    BLUE, BLUE_LIGHT, GREEN, GREEN_LIGHT, RED, RED_LIGHT,
    WHITE, GRAY_MID, GOLD, COR_EXPORTACAO, COR_IMPORTACAO,
    COR_SALDO_POSITIVO, COR_SALDO_NEGATIVO, COR_CORRENTE,
    COR_CENARIO_CONSERVADOR, COR_CENARIO_BASE, COR_CENARIO_OTIMISTA,
    COLOR_SEQUENCE, PERIODO_PASSADO, PERIODO_PRESENTE, PERIODO_PROJECAO,
    ANO_BASE_INDICE, fmt_usd, fmt_pct,
)
from data_loader import (
    load_uf_data, load_secao_data,
    compute_aggregates, compute_secao_aggregates,
    compute_index_base100, compute_growth_rates,
    get_top_secoes, get_uf_ranking, get_top_secoes_evolucao,
    compute_projections, filter_period,
)

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ═══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Dashboard Comercial Brasil\u2013Pa\u00edses Baixos",
    page_icon="\U0001f1e7\U0001f1f7",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Injetar CSS customizado
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# CARGA DE DADOS
# ═══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def load_all_data():
    """Carrega e processa todos os dados necessários."""
    df_uf = load_uf_data()
    df_secao = load_secao_data()
    agg = compute_aggregates(df_uf)
    secao_agg = compute_secao_aggregates(df_secao)
    return df_uf, df_secao, agg, secao_agg


df_uf, df_secao, agg_total, secao_agg = load_all_data()


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — NAVEGAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(
        '<div style="text-align:center; padding: 1rem 0;">'
        '<div style="font-size: 2.5rem; margin-bottom: 0.3rem;">'
        '\U0001f1e7\U0001f1f7 \U0001f91d \U0001f1f3\U0001f1f1</div>'
        '<h2 style="font-size: 1.15rem; font-weight: 600; color: #FAFAFA;'
        ' margin: 0; line-height: 1.3;">'
        'Dashboard Comercial<br>Brasil\u2013Pa\u00edses Baixos</h2>'
        '<p style="font-size: 0.78rem; color: #B0B8C4; margin-top: 0.4rem;">'
        'Dados oficiais \u00b7 Comex Stat / MDIC</p></div>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    aba_selecionada = st.radio(
        "Navega\u00e7\u00e3o",
        ABAS,
        index=0,
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.markdown(
        '<div style="font-size: 0.72rem; color: #B0B8C4; text-align: center;'
        ' padding-top: 0.5rem; line-height: 1.5;">'
        '<strong>Fonte dos dados:</strong><br>'
        'Comex Stat \u2014 MDIC<br>'
        'Minist\u00e9rio da Ind\u00fastria, Com\u00e9rcio<br>'
        'Exterior e Servi\u00e7os<br><br>'
        '<strong>Per\u00edodo:</strong> 1997\u20132025<br>'
        '<strong>Atualiza\u00e7\u00e3o:</strong> Jun/2026</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# FUNÇÕES AUXILIARES DE LAYOUT
# ═══════════════════════════════════════════════════════════════════════════════

_CHART_WIDTH = "stretch"


def show_chart(fig):
    """Exibe gráfico Plotly com configuração padrão."""
    st.plotly_chart(
        fig,
        width=_CHART_WIDTH,
        config={
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
        },
    )


def render_metric_cards(cols_data: list):
    """Renderiza cards de métricas em colunas."""
    cols = st.columns(len(cols_data))
    for col, (label, value, delta) in zip(cols, cols_data):
        col.metric(label=label, value=value, delta=delta)


# ═══════════════════════════════════════════════════════════════════════════════
# ABA 1 — PASSADO HISTÓRICO
# ═══════════════════════════════════════════════════════════════════════════════

def render_aba1():
    """Aba 1: Passado Histórico — Relação Brasil–Países Baixos."""

    st.markdown(
        '<div class="hero-header animate-in">'
        '<h1>\U0001f3db\ufe0f Passado Hist\u00f3rico: Brasil & Pa\u00edses Baixos</h1>'
        '<p>Uma rela\u00e7\u00e3o que atravessa s\u00e9culos \u2014 do per\u00edodo colonial '
        '\u00e0 parceria comercial estrat\u00e9gica</p></div>',
        unsafe_allow_html=True,
    )

    # ── Texto de contextualização ──
    st.markdown(
        '<div class="info-box animate-in">'
        'A rela\u00e7\u00e3o entre o Brasil e os Pa\u00edses Baixos \u00e9 uma das mais '
        'longevas da hist\u00f3ria diplom\u00e1tica brasileira, remontando ao per\u00edodo '
        'colonial. Desde a presen\u00e7a neerlandesa no Nordeste brasileiro no s\u00e9culo '
        'XVII at\u00e9 a consolida\u00e7\u00e3o dos Pa\u00edses Baixos como um dos principais '
        'parceiros comerciais europeus do Brasil, essa rela\u00e7\u00e3o se transformou de '
        'ocupa\u00e7\u00e3o territorial para parceria estrat\u00e9gica em com\u00e9rcio, '
        'investimento e coopera\u00e7\u00e3o tecnol\u00f3gica.</div>',
        unsafe_allow_html=True,
    )

    # ── Linha do Tempo — dados dos marcos ──
    marcos = [
        ("S\u00e9culo XVII", "Presen\u00e7a Neerlandesa no Nordeste",
         "A Companhia das \u00cdndias Ocidentais (WIC) estabeleceu presen\u00e7a "
         "no Nordeste brasileiro, iniciando uma rela\u00e7\u00e3o que marcaria a hist\u00f3ria "
         "de ambas as na\u00e7\u00f5es. O interesse pelo com\u00e9rcio de a\u00e7\u00facar e pau-brasil "
         "motivou expedi\u00e7\u00f5es e ocupa\u00e7\u00f5es.", "\u2693"),
        ("1630\u20131654", "Ocupa\u00e7\u00e3o Neerlandesa em Pernambuco",
         "Per\u00edodo do Brasil Holand\u00eas sob o governo de Maur\u00edcio de Nassau. "
         "Recife tornou-se um centro de cultura e urbanismo avan\u00e7ado. A ocupa\u00e7\u00e3o "
         "abrangeu Pernambuco, Para\u00edba, Rio Grande do Norte e partes do Cear\u00e1 e "
         "Sergipe, deixando marcas duradouras na arquitetura e cultura nordestinas.", "\U0001f3f0"),
        ("1828", "Tratado de Amizade, Navega\u00e7\u00e3o e Com\u00e9rcio",
         "Assinatura do Tratado de Amizade, Navega\u00e7\u00e3o e Com\u00e9rcio entre o Imp\u00e9rio "
         "do Brasil e o Reino dos Pa\u00edses Baixos, formalizando as rela\u00e7\u00f5es "
         "diplom\u00e1ticas e comerciais entre as duas na\u00e7\u00f5es.", "\U0001f4dc"),
        ("S\u00e9culo XX", "Fortalecimento Diplom\u00e1tico e Empresarial",
         "Estreitamento das rela\u00e7\u00f5es com aumento dos investimentos neerlandeses "
         "no Brasil, especialmente nos setores de petr\u00f3leo, g\u00e1s, alimentos e "
         "infraestrutura. Empresas como Shell, Philips e Unilever consolidaram "
         "presen\u00e7a no mercado brasileiro.", "\U0001f91d"),
        ("1997", "In\u00edcio da S\u00e9rie Hist\u00f3rica \u2014 Comex Stat",
         "In\u00edcio da s\u00e9rie estat\u00edstica de com\u00e9rcio exterior dispon\u00edvel no sistema "
         "Comex Stat do MDIC, permitindo an\u00e1lise quantitativa detalhada dos fluxos "
         "comerciais bilaterais com granularidade por produto, UF e via de transporte.", "\U0001f4ca"),
        ("2015", "Marco de Transi\u00e7\u00e3o para An\u00e1lise Contempor\u00e2nea",
         "Ponto de corte temporal que separa a an\u00e1lise hist\u00f3rica da contempor\u00e2nea "
         "neste dashboard. A partir deste ano, observa-se a configura\u00e7\u00e3o atual da "
         "pauta comercial, com os Pa\u00edses Baixos consolidados como porta de entrada "
         "de produtos brasileiros na Europa via Porto de Roterd\u00e3.", "\U0001f504"),
    ]

    # Construir HTML dos itens
    items_html = ""
    for i, (ano, titulo, desc, icone) in enumerate(marcos):
        items_html += (
            f'<div class="tl-item" style="animation-delay:{i*0.15}s">'
            f'<div class="tl-content">'
            f'<div style="font-size:1.5rem;margin-bottom:0.3rem">{icone}</div>'
            f'<div class="tl-year">{ano}</div>'
            f'<div class="tl-title">{titulo}</div>'
            f'<div class="tl-desc">{desc}</div>'
            f'</div>'
            f'<div class="tl-dot"></div>'
            f'<div class="tl-spacer"></div>'
            f'</div>'
        )

    timeline_html = (
        '<!DOCTYPE html><html><head><style>'
        'body{background:transparent;margin:0;padding:0;'
        'font-family:Inter,Segoe UI,sans-serif}'
        '.tl-wrap{position:relative;padding:20px 0}'
        '.tl-line{position:absolute;left:50%;top:0;bottom:0;width:3px;'
        'background:linear-gradient(180deg,#E87722,#2196F3,#E87722);'
        'transform:translateX(-50%);border-radius:2px}'
        '.tl-item{display:flex;align-items:center;margin:30px 0;'
        'position:relative;animation:fadeUp .6s ease-out forwards;opacity:0}'
        '.tl-item:nth-child(odd){flex-direction:row}'
        '.tl-item:nth-child(even){flex-direction:row-reverse}'
        '.tl-content{width:44%;padding:1.2rem 1.5rem;'
        'background:linear-gradient(135deg,#1B2A4A,#263B5E);'
        'border-radius:12px;border:1px solid rgba(255,255,255,.08);'
        'box-shadow:0 4px 20px rgba(0,0,0,.3);'
        'transition:transform .3s,box-shadow .3s}'
        '.tl-content:hover{transform:translateY(-3px) scale(1.01);'
        'box-shadow:0 8px 30px rgba(232,119,34,.2)}'
        '.tl-dot{width:18px;height:18px;background:#E87722;border-radius:50%;'
        'position:absolute;left:50%;transform:translateX(-50%);'
        'border:3px solid #0E1117;z-index:2;'
        'box-shadow:0 0 15px rgba(232,119,34,.4)}'
        '.tl-spacer{width:44%}'
        '.tl-year{font-size:1.1rem;font-weight:700;color:#E87722;margin-bottom:.4rem}'
        '.tl-title{font-size:.95rem;font-weight:600;color:#FAFAFA;margin-bottom:.3rem}'
        '.tl-desc{font-size:.85rem;color:#B0B8C4;line-height:1.5}'
        '@keyframes fadeUp{from{opacity:0;transform:translateY(20px)}'
        'to{opacity:1;transform:translateY(0)}}'
        '</style></head><body>'
        '<div class="tl-wrap"><div class="tl-line"></div>'
        f'{items_html}</div></body></html>'
    )

    components.html(timeline_html, height=1100, scrolling=False)

    # ── Card de destaque final ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        '<div class="highlight-card animate-in" style="text-align:center">'
        '<div style="font-size:1.1rem;font-weight:600;color:#E87722;margin-bottom:0.5rem">'
        '\U0001f310 Uma Parceria Estrat\u00e9gica Consolidada</div>'
        '<div style="font-size:0.9rem;color:#B0B8C4;line-height:1.6;max-width:700px;margin:0 auto">'
        'Hoje, os Pa\u00edses Baixos figuram entre os 10 maiores parceiros comerciais do Brasil '
        'na Europa. O Porto de Roterd\u00e3 \u2014 o maior da Europa \u2014 funciona como hub log\u00edstico '
        'para a entrada de commodities brasileiras no mercado europeu. A rela\u00e7\u00e3o bilateral '
        'movimenta bilh\u00f5es de d\u00f3lares anualmente e \u00e9 tradicionalmente super\u00e1vit\u00e1ria '
        'para o Brasil.</div></div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ABA 2 — PASSADO COM DADOS (1997–2014)
# ═══════════════════════════════════════════════════════════════════════════════

def render_aba2():
    """Aba 2: Comércio Bilateral 1997–2014."""

    st.markdown(
        '<div class="hero-header animate-in">'
        '<h1>\U0001f4ca Com\u00e9rcio Bilateral: 1997 a 2014</h1>'
        '<p>Evolu\u00e7\u00e3o dos fluxos comerciais no per\u00edodo hist\u00f3rico capturado pelo Comex Stat</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Filtrar período
    dados = filter_period(agg_total, PERIODO_PASSADO)

    # Métricas de destaque
    total_exp = dados["Exportacao"].sum()
    total_imp = dados["Importacao"].sum()
    saldo_total = total_exp - total_imp
    render_metric_cards([
        ("Exporta\u00e7\u00f5es Acumuladas (1997\u20132014)", fmt_usd(total_exp), None),
        ("Importa\u00e7\u00f5es Acumuladas (1997\u20132014)", fmt_usd(total_imp), None),
        ("Saldo Acumulado", fmt_usd(saldo_total),
         "Super\u00e1vit" if saldo_total > 0 else "D\u00e9ficit"),
    ])

    st.markdown("---")

    # ── Gráfico 1: Exportações × Importações (Barras Agrupadas) ──
    st.markdown(
        '<div class="section-header">1. Exporta\u00e7\u00f5es \u00d7 Importa\u00e7\u00f5es (1997\u20132014)</div>',
        unsafe_allow_html=True,
    )

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=dados["Ano"], y=dados["Exportacao"],
        name="Exporta\u00e7\u00f5es", marker_color=COR_EXPORTACAO,
        text=[fmt_usd(v) for v in dados["Exportacao"]],
        textposition="none",
        hovertemplate="<b>%{x}</b><br>Exporta\u00e7\u00f5es: %{text}<extra></extra>",
    ))
    fig1.add_trace(go.Bar(
        x=dados["Ano"], y=dados["Importacao"],
        name="Importa\u00e7\u00f5es", marker_color=COR_IMPORTACAO,
        text=[fmt_usd(v) for v in dados["Importacao"]],
        textposition="none",
        hovertemplate="<b>%{x}</b><br>Importa\u00e7\u00f5es: %{text}<extra></extra>",
    ))
    fig1.update_layout(
        barmode="group",
        title="Exporta\u00e7\u00f5es e Importa\u00e7\u00f5es Brasil \u2192 Pa\u00edses Baixos",
        xaxis_title="Ano", yaxis_title="Valor FOB (US$)",
        xaxis=dict(dtick=1), height=450,
        yaxis=dict(tickformat=",.0f"),
    )
    show_chart(fig1)

    # ── Gráfico 2: Saldo Comercial ──
    st.markdown(
        '<div class="section-header">2. Saldo Comercial (Exporta\u00e7\u00f5es \u2212 Importa\u00e7\u00f5es)</div>',
        unsafe_allow_html=True,
    )

    cores_saldo = [
        COR_SALDO_POSITIVO if s >= 0 else COR_SALDO_NEGATIVO
        for s in dados["SaldoComercial"]
    ]
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=dados["Ano"], y=dados["SaldoComercial"],
        marker_color=cores_saldo,
        text=[fmt_usd(v) for v in dados["SaldoComercial"]],
        textposition="outside", textfont=dict(size=10),
        hovertemplate="<b>%{x}</b><br>Saldo: %{text}<extra></extra>",
        name="Saldo Comercial",
    ))
    fig2.add_hline(y=0, line_dash="dash", line_color=GRAY_MID, line_width=1)
    fig2.update_layout(
        title="Saldo Comercial Bilateral (Super\u00e1vit \U0001f7e2 / D\u00e9ficit \U0001f534)",
        xaxis_title="Ano", yaxis_title="Saldo FOB (US$)",
        xaxis=dict(dtick=1), height=450,
        yaxis=dict(tickformat=",.0f"),
    )
    show_chart(fig2)

    # ── Gráfico 3: Corrente de Comércio (Área) ──
    st.markdown(
        '<div class="section-header">3. Corrente de Com\u00e9rcio (Exporta\u00e7\u00f5es + Importa\u00e7\u00f5es)</div>',
        unsafe_allow_html=True,
    )

    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=dados["Ano"], y=dados["CorrenteComercio"],
        fill="tozeroy", fillcolor="rgba(171,71,188,0.2)",
        line=dict(color=COR_CORRENTE, width=3),
        mode="lines+markers", marker=dict(size=7),
        name="Corrente de Com\u00e9rcio",
        text=[fmt_usd(v) for v in dados["CorrenteComercio"]],
        hovertemplate="<b>%{x}</b><br>Corrente: %{text}<extra></extra>",
    ))
    fig3.update_layout(
        title="Corrente de Com\u00e9rcio Brasil\u2013Pa\u00edses Baixos",
        xaxis_title="Ano", yaxis_title="Corrente FOB (US$)",
        xaxis=dict(dtick=1), height=450,
        yaxis=dict(tickformat=",.0f"),
    )
    show_chart(fig3)

    # ── Gráfico 4: Índice Base 100 ──
    st.markdown(
        f'<div class="section-header">4. \u00cdndice Base 100 (Ano-base: {ANO_BASE_INDICE})</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="info-box">'
        f'<strong>F\u00f3rmula:</strong> \u00cdndice = (Valor do ano atual \u00f7 Valor de {ANO_BASE_INDICE}) \u00d7 100<br>'
        f'Permite comparar a evolu\u00e7\u00e3o relativa dos fluxos de exporta\u00e7\u00e3o, importa\u00e7\u00e3o e corrente '
        f'de com\u00e9rcio, independentemente da escala absoluta de cada vari\u00e1vel.</div>',
        unsafe_allow_html=True,
    )

    idx = compute_index_base100(dados, ANO_BASE_INDICE)
    fig4 = go.Figure()
    fig4.add_trace(go.Scatter(
        x=idx["Ano"], y=idx["IndiceExportacao"],
        mode="lines+markers", name="\u00cdndice Exporta\u00e7\u00e3o",
        line=dict(color=COR_EXPORTACAO, width=3), marker=dict(size=7),
    ))
    fig4.add_trace(go.Scatter(
        x=idx["Ano"], y=idx["IndiceImportacao"],
        mode="lines+markers", name="\u00cdndice Importa\u00e7\u00e3o",
        line=dict(color=COR_IMPORTACAO, width=3), marker=dict(size=7),
    ))
    fig4.add_trace(go.Scatter(
        x=idx["Ano"], y=idx["IndiceCorrente"],
        mode="lines+markers", name="\u00cdndice Corrente de Com\u00e9rcio",
        line=dict(color=COR_CORRENTE, width=3, dash="dot"), marker=dict(size=7),
    ))
    fig4.add_hline(
        y=100, line_dash="dash", line_color=GRAY_MID, line_width=1,
        annotation_text=f"Base = 100 ({ANO_BASE_INDICE})",
        annotation_position="top right",
        annotation_font=dict(size=10, color=GRAY_MID),
    )
    fig4.update_layout(
        title=f"\u00cdndice Base 100 \u2014 Evolu\u00e7\u00e3o Comparativa (Base: {ANO_BASE_INDICE})",
        xaxis_title="Ano", yaxis_title="\u00cdndice (base 100)",
        xaxis=dict(dtick=1), height=480,
    )
    show_chart(fig4)


# ═══════════════════════════════════════════════════════════════════════════════
# ABA 3 — PRESENTE: COMÉRCIO (2015–2025)
# ═══════════════════════════════════════════════════════════════════════════════

def render_aba3():
    """Aba 3: Análise Contemporânea do Comércio Bilateral (2015–2025)."""

    st.markdown(
        '<div class="hero-header animate-in">'
        '<h1>\U0001f4c8 Com\u00e9rcio Bilateral: 2015 a 2025</h1>'
        '<p>An\u00e1lise estat\u00edstica da rela\u00e7\u00e3o comercial contempor\u00e2nea e o papel '
        'estrat\u00e9gico europeu</p></div>',
        unsafe_allow_html=True,
    )

    # ── Parágrafo institucional (Itamaraty) ──
    st.markdown(
        '<div class="info-box animate-in" style="border-left-color:#2196F3">'
        '<div style="font-weight:600;color:#2196F3;margin-bottom:0.5rem">'
        '\U0001f4cb Nota Institucional \u2014 Itamaraty</div>'
        '\u201cO per\u00edodo de 2015 a 2025 representa o recorte contempor\u00e2neo da an\u00e1lise, '
        'permitindo observar a configura\u00e7\u00e3o atual da rela\u00e7\u00e3o comercial entre Brasil '
        'e Pa\u00edses Baixos, especialmente em rela\u00e7\u00e3o ao saldo comercial, \u00e0 composi\u00e7\u00e3o '
        'da pauta exportadora e importadora e \u00e0 import\u00e2ncia dos Pa\u00edses Baixos como '
        'porta de entrada para produtos brasileiros na Europa. O Itamaraty destaca '
        'que os Pa\u00edses Baixos e seus portos s\u00e3o utilizados como porta de entrada para '
        'produtos brasileiros na Europa, e que a balan\u00e7a comercial bilateral \u00e9 '
        'tradicionalmente super\u00e1vit\u00e1ria para o Brasil.\u201d</div>',
        unsafe_allow_html=True,
    )

    # Filtrar período
    dados = filter_period(agg_total, PERIODO_PRESENTE)
    dados_gr = compute_growth_rates(dados)

    # Métricas de destaque
    ultimo_ano = dados.iloc[-1]
    penultimo_ano = dados.iloc[-2] if len(dados) > 1 else dados.iloc[-1]
    var_exp = ((ultimo_ano["Exportacao"] / penultimo_ano["Exportacao"]) - 1) * 100
    var_imp = ((ultimo_ano["Importacao"] / penultimo_ano["Importacao"]) - 1) * 100

    render_metric_cards([
        (f"Exporta\u00e7\u00f5es {int(ultimo_ano['Ano'])}",
         fmt_usd(ultimo_ano["Exportacao"]), fmt_pct(var_exp)),
        (f"Importa\u00e7\u00f5es {int(ultimo_ano['Ano'])}",
         fmt_usd(ultimo_ano["Importacao"]), fmt_pct(var_imp)),
        (f"Saldo {int(ultimo_ano['Ano'])}",
         fmt_usd(ultimo_ano["SaldoComercial"]),
         "Super\u00e1vit" if ultimo_ano["SaldoComercial"] > 0 else "D\u00e9ficit"),
        (f"Corrente {int(ultimo_ano['Ano'])}",
         fmt_usd(ultimo_ano["CorrenteComercio"]), None),
    ])

    st.markdown("---")

    # ── Gráfico 1: Painel Comparativo Exportações × Importações ──
    st.markdown(
        '<div class="section-header">1. Painel Comparativo: Exporta\u00e7\u00f5es \u00d7 Importa\u00e7\u00f5es</div>',
        unsafe_allow_html=True,
    )

    fig1 = go.Figure()
    fig1.add_trace(go.Bar(
        x=dados["Ano"], y=dados["Exportacao"],
        name="Exporta\u00e7\u00f5es", marker_color=COR_EXPORTACAO,
        text=[fmt_usd(v) for v in dados["Exportacao"]],
        textposition="none",
        hovertemplate="<b>%{x}</b><br>Exporta\u00e7\u00f5es: %{text}<extra></extra>",
    ))
    fig1.add_trace(go.Bar(
        x=dados["Ano"], y=dados["Importacao"],
        name="Importa\u00e7\u00f5es", marker_color=COR_IMPORTACAO,
        text=[fmt_usd(v) for v in dados["Importacao"]],
        textposition="none",
        hovertemplate="<b>%{x}</b><br>Importa\u00e7\u00f5es: %{text}<extra></extra>",
    ))
    fig1.update_layout(
        barmode="group",
        title="Exporta\u00e7\u00f5es e Importa\u00e7\u00f5es Brasil \u2192 Pa\u00edses Baixos (2015\u20132025)",
        xaxis_title="Ano", yaxis_title="Valor FOB (US$)",
        xaxis=dict(dtick=1), height=450,
        yaxis=dict(tickformat=",.0f"),
    )
    show_chart(fig1)

    # ── Gráfico 2: Saldo Comercial + Corrente de Comércio ──
    st.markdown(
        '<div class="section-header">2. Saldo Comercial e Corrente de Com\u00e9rcio</div>',
        unsafe_allow_html=True,
    )

    fig2 = go.Figure()
    cores_saldo = [
        COR_SALDO_POSITIVO if s >= 0 else COR_SALDO_NEGATIVO
        for s in dados["SaldoComercial"]
    ]
    fig2.add_trace(go.Bar(
        x=dados["Ano"], y=dados["SaldoComercial"],
        name="Saldo Comercial", marker_color=cores_saldo,
        text=[fmt_usd(v) for v in dados["SaldoComercial"]],
        textposition="none",
        hovertemplate="<b>%{x}</b><br>Saldo: %{text}<extra></extra>",
        yaxis="y",
    ))
    fig2.add_trace(go.Scatter(
        x=dados["Ano"], y=dados["CorrenteComercio"],
        name="Corrente de Com\u00e9rcio", line=dict(color=COR_CORRENTE, width=3),
        mode="lines+markers", marker=dict(size=8),
        text=[fmt_usd(v) for v in dados["CorrenteComercio"]],
        hovertemplate="<b>%{x}</b><br>Corrente: %{text}<extra></extra>",
        yaxis="y2",
    ))
    fig2.update_layout(
        title="Saldo Comercial (barras) e Corrente de Com\u00e9rcio (linha)",
        xaxis_title="Ano", xaxis=dict(dtick=1),
        yaxis=dict(title="Saldo FOB (US$)", tickformat=",.0f"),
        yaxis2=dict(
            title="Corrente FOB (US$)", overlaying="y", side="right",
            tickformat=",.0f", showgrid=False,
        ),
        height=470, legend=dict(x=0.01, y=0.99),
    )
    show_chart(fig2)

    # ── Gráfico 3: Taxa de Crescimento Anual (%) ──
    st.markdown(
        '<div class="section-header">3. Taxa de Crescimento Anual (%)</div>',
        unsafe_allow_html=True,
    )

    gr_plot = dados_gr.dropna(subset=["CrescimentoExportacao"]).copy()

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=gr_plot["Ano"], y=gr_plot["CrescimentoExportacao"],
        name="Crescimento Exporta\u00e7\u00f5es (%)",
        marker_color=[GREEN if v >= 0 else RED for v in gr_plot["CrescimentoExportacao"]],
        text=[fmt_pct(v) for v in gr_plot["CrescimentoExportacao"]],
        textposition="outside", textfont=dict(size=9),
        hovertemplate="<b>%{x}</b><br>Crescimento Exp: %{text}<extra></extra>",
    ))
    fig3.add_trace(go.Scatter(
        x=gr_plot["Ano"], y=gr_plot["CrescimentoImportacao"],
        name="Crescimento Importa\u00e7\u00f5es (%)",
        mode="lines+markers", line=dict(color=ORANGE, width=2.5), marker=dict(size=7),
        hovertemplate="<b>%{x}</b><br>Crescimento Imp: %{y:.1f}%<extra></extra>",
    ))
    fig3.add_hline(y=0, line_dash="dash", line_color=GRAY_MID, line_width=1)
    fig3.update_layout(
        title="Taxa de Crescimento Anual dos Fluxos Comerciais",
        xaxis_title="Ano", yaxis_title="Crescimento (%)",
        xaxis=dict(dtick=1), height=450,
    )
    show_chart(fig3)

    # ── Gráfico 4: Ranking UFs Exportadoras ──
    st.markdown(
        '<div class="section-header">4. Ranking das UFs Exportadoras para Pa\u00edses Baixos</div>',
        unsafe_allow_html=True,
    )

    uf_rank = get_uf_ranking(df_uf, PERIODO_PRESENTE, "Exportacao", top_n=15)

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        y=uf_rank["UF"], x=uf_rank["Exportacao"],
        orientation="h",
        marker=dict(
            color=uf_rank["Exportacao"],
            colorscale=[[0, NAVY_LIGHT], [0.5, BLUE], [1, ORANGE]],
        ),
        text=[fmt_usd(v) for v in uf_rank["Exportacao"]],
        textposition="auto", textfont=dict(size=10),
        hovertemplate="<b>%{y}</b><br>Exporta\u00e7\u00f5es: %{text}<extra></extra>",
    ))
    fig4.update_layout(
        title="Top 15 UFs \u2014 Exporta\u00e7\u00f5es Acumuladas para Pa\u00edses Baixos (2015\u20132025)",
        xaxis_title="Valor FOB Acumulado (US$)",
        yaxis=dict(categoryorder="total ascending"),
        height=550, xaxis=dict(tickformat=",.0f"),
    )
    show_chart(fig4)


# ═══════════════════════════════════════════════════════════════════════════════
# ABA 4 — PRODUTOS E ESTRUTURA COMERCIAL
# ═══════════════════════════════════════════════════════════════════════════════

def render_aba4():
    """Aba 4: Produtos e Estrutura Comercial (2015–2025)."""

    st.markdown(
        '<div class="hero-header animate-in">'
        '<h1>\U0001f3ed Produtos e Estrutura Comercial</h1>'
        '<p>Perfil da pauta comercial bilateral \u2014 Assimetria e complementaridade '
        'econ\u00f4mica (2015\u20132025)</p></div>',
        unsafe_allow_html=True,
    )

    # ── Seção de Exportações ──
    st.markdown(
        '<div class="section-header">\U0001f4e6 Exporta\u00e7\u00f5es Brasileiras para os Pa\u00edses Baixos</div>',
        unsafe_allow_html=True,
    )

    col_exp1, col_exp2 = st.columns([1, 1])

    top_exp = get_top_secoes(secao_agg, PERIODO_PRESENTE, "Exportacao", top_n=10)

    with col_exp1:
        st.markdown("##### Top 10 Categorias Exportadas (Acumulado 2015\u20132025)")
        top_exp_display = top_exp.copy()
        top_exp_display["Label"] = top_exp_display["DescricaoSecao"].apply(
            lambda x: x[:55] + "\u2026" if len(str(x)) > 55 else x
        )
        fig_exp_bar = go.Figure()
        fig_exp_bar.add_trace(go.Bar(
            y=top_exp_display["Label"], x=top_exp_display["Exportacao"],
            orientation="h",
            marker=dict(
                color=top_exp_display["Exportacao"],
                colorscale=[[0, BLUE_LIGHT], [1, BLUE]],
            ),
            text=[fmt_usd(v) for v in top_exp_display["Exportacao"]],
            textposition="auto", textfont=dict(size=9),
            hovertemplate="<b>%{y}</b><br>Exporta\u00e7\u00e3o: %{text}<extra></extra>",
        ))
        fig_exp_bar.update_layout(
            yaxis=dict(categoryorder="total ascending"),
            height=450, margin=dict(l=10),
            xaxis=dict(tickformat=",.0f"),
        )
        show_chart(fig_exp_bar)

    with col_exp2:
        st.markdown("##### Treemap da Pauta Exportadora")
        top_exp_tree = top_exp.copy()
        top_exp_tree["Label_tree"] = top_exp_tree["DescricaoSecao"].apply(
            lambda x: x[:40] + "\u2026" if len(str(x)) > 40 else x
        )
        fig_exp_tree = px.treemap(
            top_exp_tree, path=["Label_tree"], values="Exportacao",
            color="Exportacao",
            color_continuous_scale=[[0, NAVY_LIGHT], [0.5, BLUE], [1, BLUE_LIGHT]],
        )
        fig_exp_tree.update_layout(height=450, margin=dict(l=10, r=10, t=30, b=10))
        fig_exp_tree.update_traces(
            textinfo="label+percent root",
            hovertemplate="<b>%{label}</b><br>Valor: US$ %{value:,.0f}<br>"
                          "Participa\u00e7\u00e3o: %{percentRoot:.1%}<extra></extra>",
        )
        show_chart(fig_exp_tree)

    st.markdown("---")

    # ── Seção de Importações ──
    st.markdown(
        '<div class="section-header">\U0001f4e5 Importa\u00e7\u00f5es Brasileiras dos Pa\u00edses Baixos</div>',
        unsafe_allow_html=True,
    )

    col_imp1, col_imp2 = st.columns([1, 1])

    top_imp = get_top_secoes(secao_agg, PERIODO_PRESENTE, "Importacao", top_n=10)

    with col_imp1:
        st.markdown("##### Top 10 Categorias Importadas (Acumulado 2015\u20132025)")
        top_imp_display = top_imp.copy()
        top_imp_display["Label"] = top_imp_display["DescricaoSecao"].apply(
            lambda x: x[:55] + "\u2026" if len(str(x)) > 55 else x
        )
        fig_imp_bar = go.Figure()
        fig_imp_bar.add_trace(go.Bar(
            y=top_imp_display["Label"], x=top_imp_display["Importacao"],
            orientation="h",
            marker=dict(
                color=top_imp_display["Importacao"],
                colorscale=[[0, ORANGE_LIGHT], [1, ORANGE]],
            ),
            text=[fmt_usd(v) for v in top_imp_display["Importacao"]],
            textposition="auto", textfont=dict(size=9),
            hovertemplate="<b>%{y}</b><br>Importa\u00e7\u00e3o: %{text}<extra></extra>",
        ))
        fig_imp_bar.update_layout(
            yaxis=dict(categoryorder="total ascending"),
            height=450, margin=dict(l=10),
            xaxis=dict(tickformat=",.0f"),
        )
        show_chart(fig_imp_bar)

    with col_imp2:
        st.markdown("##### Treemap da Pauta Importadora")
        top_imp_tree = top_imp.copy()
        top_imp_tree["Label_tree"] = top_imp_tree["DescricaoSecao"].apply(
            lambda x: x[:40] + "\u2026" if len(str(x)) > 40 else x
        )
        fig_imp_tree = px.treemap(
            top_imp_tree, path=["Label_tree"], values="Importacao",
            color="Importacao",
            color_continuous_scale=[[0, NAVY_LIGHT], [0.5, ORANGE], [1, ORANGE_LIGHT]],
        )
        fig_imp_tree.update_layout(height=450, margin=dict(l=10, r=10, t=30, b=10))
        fig_imp_tree.update_traces(
            textinfo="label+percent root",
            hovertemplate="<b>%{label}</b><br>Valor: US$ %{value:,.0f}<br>"
                          "Participa\u00e7\u00e3o: %{percentRoot:.1%}<extra></extra>",
        )
        show_chart(fig_imp_tree)

    st.markdown("---")

    # ── Evolução Temporal do Top 3 ──
    st.markdown(
        '<div class="section-header">\U0001f4c8 Evolu\u00e7\u00e3o Temporal do Top 3 de cada Pauta</div>',
        unsafe_allow_html=True,
    )

    col_ev1, col_ev2 = st.columns([1, 1])

    with col_ev1:
        st.markdown("##### Top 3 Categorias Exportadas \u2014 Evolu\u00e7\u00e3o Anual")
        evo_exp = get_top_secoes_evolucao(secao_agg, PERIODO_PRESENTE, "Exportacao", 3)
        fig_evo_exp = go.Figure()
        for i, (_, grp) in enumerate(evo_exp.groupby("CodigoSecao")):
            label = grp["DescricaoSecao"].iloc[0]
            label_short = label[:45] + "\u2026" if len(str(label)) > 45 else label
            fig_evo_exp.add_trace(go.Scatter(
                x=grp["Ano"], y=grp["Exportacao"],
                mode="lines+markers", name=label_short,
                line=dict(width=2.5, color=COLOR_SEQUENCE[i]),
                marker=dict(size=6),
                hovertemplate=f"<b>{label_short}</b><br>"
                              "Ano: %{x}<br>Exporta\u00e7\u00e3o: US$ %{y:,.0f}<extra></extra>",
            ))
        fig_evo_exp.update_layout(
            height=420, xaxis=dict(dtick=1),
            yaxis=dict(tickformat=",.0f"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.35, font=dict(size=9)),
        )
        show_chart(fig_evo_exp)

    with col_ev2:
        st.markdown("##### Top 3 Categorias Importadas \u2014 Evolu\u00e7\u00e3o Anual")
        evo_imp = get_top_secoes_evolucao(secao_agg, PERIODO_PRESENTE, "Importacao", 3)
        fig_evo_imp = go.Figure()
        for i, (_, grp) in enumerate(evo_imp.groupby("CodigoSecao")):
            label = grp["DescricaoSecao"].iloc[0]
            label_short = label[:45] + "\u2026" if len(str(label)) > 45 else label
            fig_evo_imp.add_trace(go.Scatter(
                x=grp["Ano"], y=grp["Importacao"],
                mode="lines+markers", name=label_short,
                line=dict(width=2.5, color=COLOR_SEQUENCE[i + 3]),
                marker=dict(size=6),
                hovertemplate=f"<b>{label_short}</b><br>"
                              "Ano: %{x}<br>Importa\u00e7\u00e3o: US$ %{y:,.0f}<extra></extra>",
            ))
        fig_evo_imp.update_layout(
            height=420, xaxis=dict(dtick=1),
            yaxis=dict(tickformat=",.0f"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.35, font=dict(size=9)),
        )
        show_chart(fig_evo_imp)

    # ── Texto Analítico ──
    st.markdown("---")
    st.markdown(
        '<div class="highlight-card animate-in">'
        '<div style="font-weight:600;color:#E87722;margin-bottom:0.5rem;font-size:1rem">'
        '\U0001f4dd An\u00e1lise da Pauta Comercial</div>'
        '<div style="font-size:0.9rem;color:#E0E0E0;line-height:1.7">'
        'A rela\u00e7\u00e3o comercial Brasil\u2013Pa\u00edses Baixos apresenta um perfil de '
        '<strong>complementaridade assim\u00e9trica</strong>. As <strong>exporta\u00e7\u00f5es brasileiras</strong> '
        's\u00e3o fortemente concentradas em <strong>commodities agr\u00edcolas e minerais</strong>: '
        'produtos como soja e derivados, min\u00e9rio de ferro, \u00f3leos brutos de petr\u00f3leo, caf\u00e9, '
        'carnes e celulose dominam a pauta exportadora, refletindo a voca\u00e7\u00e3o prim\u00e1rio-exportadora '
        'do Brasil no com\u00e9rcio bilateral.<br><br>'
        'Em contrapartida, as <strong>importa\u00e7\u00f5es vindas dos Pa\u00edses Baixos</strong> s\u00e3o '
        'compostas por <strong>produtos de maior valor agregado</strong>: produtos qu\u00edmicos '
        'e farmac\u00eauticos, combust\u00edveis refinados, fertilizantes, m\u00e1quinas e equipamentos, '
        'instrumentos de precis\u00e3o e produtos industriais de alto conte\u00fado tecnol\u00f3gico. '
        'Essa assimetria \u00e9 caracter\u00edstica do perfil de com\u00e9rcio entre economias em '
        'desenvolvimento e economias avan\u00e7adas.</div></div>',
        unsafe_allow_html=True,
    )

    # ── Nota de Destaque Histórico (2023) ──
    st.markdown(
        '<div class="info-box animate-in" style="border-left-color:#FFD700">'
        '<div style="font-weight:600;color:#FFD700;margin-bottom:0.4rem">'
        '\u2b50 Destaque 2023 \u2014 Dados do Itamaraty</div>'
        '\u201cEm 2023, segundo dados do Itamaraty, os principais produtos exportados pelo Brasil '
        'para os Pa\u00edses Baixos foram <strong>\u00f3leos brutos de petr\u00f3leo, farelos de soja e '
        'min\u00e9rio de ferro</strong>; j\u00e1 as importa\u00e7\u00f5es brasileiras inclu\u00edram '
        '<strong>\u00f3leos combust\u00edveis, fertilizantes qu\u00edmicos e produtos da ind\u00fastria '
        'de transforma\u00e7\u00e3o</strong>.\u201d</div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ABA 5 — PROJEÇÃO (2026–2030)
# ═══════════════════════════════════════════════════════════════════════════════

def render_aba5():
    """Aba 5: Projeções do Comércio Bilateral (2026–2030)."""

    st.markdown(
        '<div class="hero-header animate-in">'
        '<h1>\U0001f52e Proje\u00e7\u00e3o: 2026 a 2030</h1>'
        '<p>Modelagem do futuro comercial bilateral atrav\u00e9s de cen\u00e1rios econ\u00f4micos</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    # ── Descrição dos Cenários ──
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f'<div class="highlight-card" style="border-color:{COR_CENARIO_CONSERVADOR}40">'
            f'<div style="font-weight:600;color:{COR_CENARIO_CONSERVADOR};'
            f'margin-bottom:0.4rem;font-size:1rem">'
            f'\u26a0\ufe0f Cen\u00e1rio Conservador</div>'
            f'<div style="font-size:0.82rem;color:#B0B8C4;line-height:1.6">'
            f'Baixo crescimento europeu, queda ou estabilidade nos pre\u00e7os de commodities, '
            f'barreiras ambientais e regulat\u00f3rias mais r\u00edgidas da UE (CBAM, desmatamento). '
            f'Menor crescimento da corrente comercial.</div></div>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f'<div class="highlight-card" style="border-color:{COR_CENARIO_BASE}40">'
            f'<div style="font-weight:600;color:{COR_CENARIO_BASE};'
            f'margin-bottom:0.4rem;font-size:1rem">'
            f'\U0001f4ca Cen\u00e1rio Base</div>'
            f'<div style="font-size:0.82rem;color:#B0B8C4;line-height:1.6">'
            f'Manuten\u00e7\u00e3o da tend\u00eancia estat\u00edstica recente (2015\u20132025). Balan\u00e7a '
            f'comercial continuamente super\u00e1vit\u00e1ria para o Brasil. Pa\u00edses Baixos '
            f'como principal hub log\u00edstico europeu. Pauta concentrada em commodities.</div></div>',
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f'<div class="highlight-card" style="border-color:{COR_CENARIO_OTIMISTA}40">'
            f'<div style="font-weight:600;color:{COR_CENARIO_OTIMISTA};'
            f'margin-bottom:0.4rem;font-size:1rem">'
            f'\U0001f680 Cen\u00e1rio Otimista</div>'
            f'<div style="font-size:0.82rem;color:#B0B8C4;line-height:1.6">'
            f'Aumento da demanda europeia por alimentos e biocombust\u00edveis, crescimento '
            f'de produtos sustent\u00e1veis (cr\u00e9ditos de carbono, H\u2082 verde), maior '
            f'integra\u00e7\u00e3o comercial e diversifica\u00e7\u00e3o da pauta exportadora.</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ── Gráfico 1: Séries Temporais Estendidas com Projeções ──
    st.markdown(
        '<div class="section-header">1. S\u00e9ries Temporais com Proje\u00e7\u00e3o por Cen\u00e1rio</div>',
        unsafe_allow_html=True,
    )

    dados_presente = filter_period(agg_total, PERIODO_PRESENTE)
    proj = compute_projections(agg_total)

    metrica = st.selectbox(
        "Selecione a m\u00e9trica para proje\u00e7\u00e3o:",
        ["Corrente de Com\u00e9rcio", "Exporta\u00e7\u00f5es", "Importa\u00e7\u00f5es", "Saldo Comercial"],
        index=0,
    )

    mapa_metrica = {
        "Corrente de Com\u00e9rcio": "CorrenteComercio",
        "Exporta\u00e7\u00f5es": "Exportacao",
        "Importa\u00e7\u00f5es": "Importacao",
        "Saldo Comercial": "SaldoComercial",
    }
    col_metrica = mapa_metrica[metrica]

    fig_proj = go.Figure()

    # Série real (2015–2025)
    fig_proj.add_trace(go.Scatter(
        x=dados_presente["Ano"], y=dados_presente[col_metrica],
        mode="lines+markers", name="Dados Reais (2015\u20132025)",
        line=dict(color=WHITE, width=3),
        marker=dict(size=7, color=WHITE),
        hovertemplate="<b>%{x}</b><br>Valor: US$ %{y:,.0f}<extra></extra>",
    ))

    cenario_cores = {
        "Conservador": COR_CENARIO_CONSERVADOR,
        "Base": COR_CENARIO_BASE,
        "Otimista": COR_CENARIO_OTIMISTA,
    }
    cenario_dash = {
        "Conservador": "dot",
        "Base": "dash",
        "Otimista": "dashdot",
    }

    for cenario in ["Conservador", "Base", "Otimista"]:
        proj_c = proj[proj["Cenario"] == cenario].copy()
        ponto_conexao = pd.DataFrame([{
            "Ano": 2025,
            col_metrica: float(dados_presente.iloc[-1][col_metrica]),
        }])
        proj_c_plot = pd.concat(
            [ponto_conexao, proj_c[["Ano", col_metrica]]], ignore_index=True
        )

        fig_proj.add_trace(go.Scatter(
            x=proj_c_plot["Ano"], y=proj_c_plot[col_metrica],
            mode="lines+markers",
            name=f"Cen\u00e1rio {cenario}",
            line=dict(
                color=cenario_cores[cenario], width=2.5,
                dash=cenario_dash[cenario],
            ),
            marker=dict(size=6),
            hovertemplate=f"<b>Cen\u00e1rio {cenario}</b><br>"
                          "Ano: %{x}<br>Valor: US$ %{y:,.0f}<extra></extra>",
        ))

    fig_proj.add_vline(
        x=2025.5, line_dash="dash", line_color=GRAY_MID, line_width=1,
        annotation_text="\u2190 Real | Proje\u00e7\u00e3o \u2192",
        annotation_position="top",
        annotation_font=dict(size=10, color=GRAY_MID),
    )
    fig_proj.update_layout(
        title=f"{metrica} \u2014 S\u00e9rie Real + Proje\u00e7\u00e3o 2026\u20132030",
        xaxis_title="Ano", yaxis_title="Valor FOB (US$)",
        xaxis=dict(dtick=1, range=[2014.5, 2030.5]),
        height=520, yaxis=dict(tickformat=",.0f"),
    )
    show_chart(fig_proj)

    # ── Tabela de Valores Projetados ──
    st.markdown("##### \U0001f4cb Valores Projetados por Cen\u00e1rio")

    proj_display = proj.copy()
    for col in ["Exportacao", "Importacao", "SaldoComercial", "CorrenteComercio"]:
        proj_display[col] = proj_display[col].apply(fmt_usd)
    proj_pivot = proj_display.pivot(
        index="Cenario", columns="Ano", values=col_metrica,
    )
    st.dataframe(proj_pivot, width="stretch", height=160)

    st.markdown("---")

    # ── Gráfico/Matriz de Oportunidades e Riscos ──
    st.markdown(
        '<div class="section-header">2. Matriz de Oportunidades e Riscos</div>',
        unsafe_allow_html=True,
    )

    col_opp, col_risk = st.columns(2)

    with col_opp:
        st.markdown(
            '<div class="highlight-card" style="border-color:rgba(76,175,80,0.4)">'
            '<div style="font-weight:700;color:#4CAF50;font-size:1.1rem;'
            'margin-bottom:0.8rem;text-align:center">'
            '\u2705 Oportunidades</div>'
            '<div class="matrix-cell matrix-opportunity">'
            '<strong>\U0001f33e Seguran\u00e7a Alimentar</strong><br>'
            'Europa busca diversificar fornecedores de alimentos. '
            'Brasil \u00e9 l\u00edder global em prote\u00ednas e gr\u00e3os.</div>'
            '<div class="matrix-cell matrix-opportunity">'
            '<strong>\u26a1 Transi\u00e7\u00e3o Energ\u00e9tica</strong><br>'
            'Demanda crescente por biocombust\u00edveis, etanol e '
            'hidrog\u00eanio verde \u2014 \u00e1reas de vantagem brasileira.</div>'
            '<div class="matrix-cell matrix-opportunity">'
            '<strong>\U0001f33f Cr\u00e9ditos de Carbono</strong><br>'
            'Brasil possui enorme potencial florestal para '
            'gera\u00e7\u00e3o de cr\u00e9ditos de carbono no mercado europeu.</div>'
            '<div class="matrix-cell matrix-opportunity">'
            '<strong>\U0001f6a2 Hub Log\u00edstico Roterd\u00e3</strong><br>'
            'Consolida\u00e7\u00e3o dos Pa\u00edses Baixos como porta de entrada '
            'para toda a Europa via Porto de Roterd\u00e3.</div>'
            '<div class="matrix-cell matrix-opportunity">'
            '<strong>\U0001f3ed Diversifica\u00e7\u00e3o da Pauta</strong><br>'
            'Potencial de exporta\u00e7\u00e3o de produtos semimanufaturados '
            'e manufaturados com maior valor agregado.</div></div>',
            unsafe_allow_html=True,
        )

    with col_risk:
        st.markdown(
            '<div class="highlight-card" style="border-color:rgba(229,57,53,0.4)">'
            '<div style="font-weight:700;color:#E53935;font-size:1.1rem;'
            'margin-bottom:0.8rem;text-align:center">'
            '\u26a0\ufe0f Riscos</div>'
            '<div class="matrix-cell matrix-risk">'
            '<strong>\U0001f30d CBAM \u2014 Mecanismo de Ajuste de Carbono</strong><br>'
            'Taxa\u00e7\u00e3o europeia sobre importa\u00e7\u00f5es com alta pegada de '
            'carbono pode afetar exporta\u00e7\u00f5es brasileiras.</div>'
            '<div class="matrix-cell matrix-risk">'
            '<strong>\U0001f333 Regula\u00e7\u00e3o de Desmatamento (EUDR)</strong><br>'
            'Exig\u00eancias de rastreabilidade podem impor barreiras '
            'a commodities agr\u00edcolas brasileiras.</div>'
            '<div class="matrix-cell matrix-risk">'
            '<strong>\U0001f4c9 Volatilidade de Commodities</strong><br>'
            'Depend\u00eancia de poucos produtos prim\u00e1rios torna a '
            'balan\u00e7a vulner\u00e1vel a choques de pre\u00e7os.</div>'
            '<div class="matrix-cell matrix-risk">'
            '<strong>\U0001f3e6 Desacelera\u00e7\u00e3o Europeia</strong><br>'
            'Recess\u00e3o ou baixo crescimento da zona do euro '
            'reduziria a demanda por importa\u00e7\u00f5es brasileiras.</div>'
            '<div class="matrix-cell matrix-risk">'
            '<strong>\U0001f504 Concentra\u00e7\u00e3o da Pauta</strong><br>'
            'Alta concentra\u00e7\u00e3o em commodities limita o potencial '
            'de crescimento sustent\u00e1vel de longo prazo.</div></div>',
            unsafe_allow_html=True,
        )

    # ── Heatmap visual de impacto ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("##### \U0001f5fa\ufe0f Matriz de Impacto por Cen\u00e1rio")

    fatores = [
        "Demanda Europeia\npor Alimentos",
        "Pre\u00e7os de\nCommodities",
        "Barreiras\nAmbientais (UE)",
        "Transi\u00e7\u00e3o\nEnerg\u00e9tica",
        "Diversifica\u00e7\u00e3o\nda Pauta",
    ]
    impacto = np.array([
        [1, 2, 3],
        [-1, 1, 2],
        [-2, -1, 0],
        [0, 1, 3],
        [-1, 0, 2],
    ])

    fig_heat = go.Figure(data=go.Heatmap(
        z=impacto,
        x=["Conservador", "Base", "Otimista"],
        y=fatores,
        colorscale=[
            [0, RED], [0.25, RED_LIGHT], [0.5, GRAY_MID],
            [0.75, GREEN_LIGHT], [1, GREEN],
        ],
        zmid=0, text=impacto, texttemplate="%{text}",
        textfont=dict(size=14, color=WHITE),
        hovertemplate="Fator: %{y}<br>Cen\u00e1rio: %{x}<br>Impacto: %{z}<extra></extra>",
        colorbar=dict(
            title="Impacto",
            tickvals=[-2, -1, 0, 1, 2, 3],
            ticktext=["Muito\nnegativo", "Negativo", "Neutro",
                       "Positivo", "Forte\npositivo", "Muito\nforte"],
        ),
    ))
    fig_heat.update_layout(
        title="Matriz de Impacto dos Fatores por Cen\u00e1rio Econ\u00f4mico",
        height=420, yaxis=dict(tickfont=dict(size=11)),
    )
    show_chart(fig_heat)

    # ── Nota metodológica ──
    st.markdown(
        '<div class="info-box animate-in" style="border-left-color:#B0B8C4;margin-top:1rem">'
        '<div style="font-weight:600;color:#B0B8C4;margin-bottom:0.3rem;font-size:0.85rem">'
        '\U0001f4d0 Nota Metodol\u00f3gica</div>'
        '<div style="font-size:0.8rem;color:#9AA0A8;line-height:1.6">'
        'As proje\u00e7\u00f5es s\u00e3o baseadas em taxas de crescimento anual aplicadas sobre os valores reais '
        'observados em 2025. O <strong>Cen\u00e1rio Conservador</strong> aplica taxas de \u22122% a +1% a.a., '
        'o <strong>Cen\u00e1rio Base</strong> aplica taxas de +3% a +4,5% a.a. (compat\u00edveis com a '
        'tend\u00eancia recente), e o <strong>Cen\u00e1rio Otimista</strong> aplica taxas de +7% a +10% a.a. '
        'Esta modelagem \u00e9 simplificada e n\u00e3o substitui modelos econom\u00e9tricos completos. '
        'Os dados de 2026 nos arquivos-fonte s\u00e3o parciais e foram exclu\u00eddos da an\u00e1lise.</div></div>',
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ROTEAMENTO DE ABAS
# ═══════════════════════════════════════════════════════════════════════════════

if aba_selecionada == ABAS[0]:
    render_aba1()
elif aba_selecionada == ABAS[1]:
    render_aba2()
elif aba_selecionada == ABAS[2]:
    render_aba3()
elif aba_selecionada == ABAS[3]:
    render_aba4()
elif aba_selecionada == ABAS[4]:
    render_aba5()

# ── Footer ──
st.markdown("---")
st.markdown(
    '<div style="text-align:center;font-size:0.75rem;color:#6B7280;padding:0.5rem 0 1rem 0">'
    'Dashboard desenvolvido com Streamlit & Plotly \u00b7 Dados: Comex Stat / MDIC \u00b7 '
    'Refer\u00eancias institucionais: Itamaraty (MRE) \u00b7 Brasil \U0001f1e7\U0001f1f7 '
    '& Pa\u00edses Baixos \U0001f1f3\U0001f1f1</div>',
    unsafe_allow_html=True,
)
