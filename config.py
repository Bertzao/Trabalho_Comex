"""
config.py — Configuração visual e constantes do dashboard Brasil–Países Baixos.

Paleta profissional: azul-marinho, cinza claro, laranja acento, azul destaque.
Define template Plotly customizado e utilitários de formatação.
"""

import plotly.graph_objects as go
import plotly.io as pio

# ═══════════════════════════════════════════════════════════════════════════════
# PALETA DE CORES
# ═══════════════════════════════════════════════════════════════════════════════
NAVY = "#1B2A4A"
NAVY_DARK = "#0E1117"
NAVY_LIGHT = "#263B5E"
GRAY_LIGHT = "#F0F2F6"
GRAY_MID = "#B0B8C4"
ORANGE = "#E87722"
ORANGE_LIGHT = "#F5A623"
BLUE = "#2196F3"
BLUE_LIGHT = "#64B5F6"
GREEN = "#4CAF50"
GREEN_LIGHT = "#81C784"
RED = "#E53935"
RED_LIGHT = "#EF5350"
WHITE = "#FAFAFA"
GOLD = "#FFD700"

# Cores para exportação / importação
COR_EXPORTACAO = BLUE
COR_IMPORTACAO = ORANGE
COR_SALDO_POSITIVO = GREEN
COR_SALDO_NEGATIVO = RED
COR_CORRENTE = "#AB47BC"  # Roxo

# Cores dos cenários de projeção
COR_CENARIO_CONSERVADOR = RED_LIGHT
COR_CENARIO_BASE = BLUE
COR_CENARIO_OTIMISTA = GREEN

# Sequência de cores para gráficos múltiplos
COLOR_SEQUENCE = [
    BLUE, ORANGE, GREEN, "#AB47BC", GOLD,
    "#26C6DA", "#FF7043", "#66BB6A", "#5C6BC0", "#EC407A",
]

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════════════
ANO_BASE_INDICE = 1997
PERIODO_PASSADO = (1997, 2014)
PERIODO_PRESENTE = (2015, 2025)
PERIODO_PROJECAO = (2026, 2030)

ABAS = [
    "🏛️ Passado Histórico",
    "📊 Passado com Dados (1997–2014)",
    "📈 Presente: Comércio (2015–2025)",
    "🏭 Presente: Produtos e Estrutura",
    "🔮 Projeção (2026–2030)",
]

# Caminhos dos arquivos de dados
ARQUIVO_UF = "H_EXPORTACAO_E IMPORTACAO_GERAL_1997-01_2026-12_DT20260624.xlsx"
ARQUIVO_SECAO = "H_EXPORTACAO_E IMPORTACAO_GERAL_1997-01_2026-12_DT20260624 (1).xlsx"
ARQUIVO_HISTORICO = "H_EXPORTACAO_E IMPORTACAO_DADOS HISTORICOS_1989-01_1996-12_DT20260624.xlsx"
ARQUIVO_DETALHADO = "V_EXPORTACAO_E IMPORTACAO_GERAL_1997-01_2026-12_DT20260624.xlsx"

# ── Novas planilhas (Julho/2026) ──
# Planilha com dados de Exportação e Importação por URF (portos, aeroportos, postos de fronteira)
ARQUIVO_URF = "H_EXPORTACAO_E IMPORTACAO_GERAL_1997-01_2026-12_DT20260701.xlsx"
# Planilha com detalhamento de produtos por hierarquia SH (SH2, SH4, SH6) + Seção NCM
ARQUIVO_SH_DETALHADO = "H_EXPORTACAO_GERAL_1997-01_2026-12_DT20260701.xlsx"


# ═══════════════════════════════════════════════════════════════════════════════
# FORMATAÇÃO
# ═══════════════════════════════════════════════════════════════════════════════

def fmt_usd(valor: float) -> str:
    """Formata valor em USD com separadores de milhar."""
    if abs(valor) >= 1e9:
        return f"US$ {valor / 1e9:,.2f} bi"
    elif abs(valor) >= 1e6:
        return f"US$ {valor / 1e6:,.1f} mi"
    else:
        return f"US$ {valor:,.0f}"


def fmt_pct(valor: float) -> str:
    """Formata percentual."""
    return f"{valor:+.1f}%"


# ═══════════════════════════════════════════════════════════════════════════════
# TEMPLATE PLOTLY CUSTOMIZADO
# ═══════════════════════════════════════════════════════════════════════════════

PLOTLY_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        font=dict(family="Inter, Segoe UI, sans-serif", color=WHITE, size=13),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        colorway=COLOR_SEQUENCE,
        title=dict(font=dict(size=18, color=WHITE), x=0.5, xanchor="center"),
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.08)",
            linecolor="rgba(255,255,255,0.2)",
            zerolinecolor="rgba(255,255,255,0.15)",
            tickfont=dict(size=11),
        ),
        yaxis=dict(
            gridcolor="rgba(255,255,255,0.08)",
            linecolor="rgba(255,255,255,0.2)",
            zerolinecolor="rgba(255,255,255,0.15)",
            tickfont=dict(size=11),
        ),
        legend=dict(
            bgcolor="rgba(27,42,74,0.7)",
            bordercolor="rgba(255,255,255,0.15)",
            borderwidth=1,
            font=dict(size=11),
        ),
        hoverlabel=dict(
            bgcolor=NAVY,
            font_size=12,
            font_family="Inter, Segoe UI, sans-serif",
        ),
        margin=dict(l=60, r=30, t=60, b=50),
    )
)

pio.templates["dashboard_custom"] = PLOTLY_TEMPLATE
pio.templates.default = "dashboard_custom"


# ═══════════════════════════════════════════════════════════════════════════════
# ESTILOS CSS CUSTOMIZADOS PARA STREAMLIT
# ═══════════════════════════════════════════════════════════════════════════════

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* ─── Reset e Base ─── */
    html, body, [class*="st-"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* ─── Sidebar ─── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B2A4A 0%, #0E1925 100%);
    }
    [data-testid="stSidebar"] .stRadio label {
        font-size: 0.95rem;
        padding: 0.5rem 0;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        color: #E87722;
    }

    /* ─── Cards / Metrics ─── */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1B2A4A 0%, #263B5E 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    }
    [data-testid="stMetricValue"] {
        font-weight: 600;
        font-size: 1.4rem !important;
    }

    /* ─── Tabs ─── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    /* ─── Dividers ─── */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(232,119,34,0.4), transparent);
        margin: 1.5rem 0;
    }

    /* ─── Tooltip / Info boxes ─── */
    .info-box {
        background: linear-gradient(135deg, #1B2A4A 0%, #1E3352 100%);
        border-left: 4px solid #E87722;
        border-radius: 0 10px 10px 0;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
        font-size: 0.95rem;
        line-height: 1.6;
        color: #E0E0E0;
    }

    /* ─── Timeline ─── */
    .timeline-container {
        position: relative;
        padding: 20px 0;
    }
    .timeline-line {
        position: absolute;
        left: 50%;
        top: 0;
        bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, #E87722, #2196F3, #E87722);
        transform: translateX(-50%);
        border-radius: 2px;
    }
    .timeline-item {
        display: flex;
        align-items: center;
        margin: 30px 0;
        position: relative;
    }
    .timeline-item:nth-child(odd) {
        flex-direction: row;
    }
    .timeline-item:nth-child(even) {
        flex-direction: row-reverse;
    }
    .timeline-content {
        width: 44%;
        padding: 1.2rem 1.5rem;
        background: linear-gradient(135deg, #1B2A4A 0%, #263B5E 100%);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .timeline-content:hover {
        transform: translateY(-3px) scale(1.01);
        box-shadow: 0 8px 30px rgba(232,119,34,0.2);
    }
    .timeline-dot {
        width: 18px;
        height: 18px;
        background: #E87722;
        border-radius: 50%;
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
        border: 3px solid #0E1117;
        z-index: 2;
        box-shadow: 0 0 15px rgba(232,119,34,0.4);
    }
    .timeline-spacer {
        width: 44%;
    }
    .timeline-year {
        font-size: 1.1rem;
        font-weight: 700;
        color: #E87722;
        margin-bottom: 0.4rem;
    }
    .timeline-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #FAFAFA;
        margin-bottom: 0.3rem;
    }
    .timeline-desc {
        font-size: 0.85rem;
        color: #B0B8C4;
        line-height: 1.5;
    }

    /* ─── Header Hero ─── */
    .hero-header {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 1rem;
    }
    .hero-header h1 {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #E87722, #FFD700);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
    }
    .hero-header p {
        color: #B0B8C4;
        font-size: 1rem;
    }

    /* ─── Section headers ─── */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #FAFAFA;
        border-bottom: 2px solid #E87722;
        padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem 0;
    }

    /* ─── Highlight cards ─── */
    .highlight-card {
        background: linear-gradient(135deg, #1B2A4A 0%, #263B5E 100%);
        border: 1px solid rgba(232,119,34,0.3);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
    }

    /* ─── Opportunity/Risk matrix ─── */
    .matrix-cell {
        padding: 1rem;
        border-radius: 8px;
        margin: 0.3rem;
        text-align: center;
        font-size: 0.85rem;
        line-height: 1.4;
    }
    .matrix-opportunity {
        background: linear-gradient(135deg, rgba(76,175,80,0.2), rgba(76,175,80,0.1));
        border: 1px solid rgba(76,175,80,0.3);
        color: #81C784;
    }
    .matrix-risk {
        background: linear-gradient(135deg, rgba(229,57,53,0.2), rgba(229,57,53,0.1));
        border: 1px solid rgba(229,57,53,0.3);
        color: #EF5350;
    }

    /* ─── Animations ─── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animate-in {
        animation: fadeInUp 0.6s ease-out forwards;
    }
</style>
"""
