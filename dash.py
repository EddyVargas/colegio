import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# ============================================================
# CONFIGURAÇÃO
# ============================================================

st.set_page_config(
    page_title="Dashboard de Vendas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

ARQUIVO = "vendas.csv"

# Paleta laranja
LARANJA = "#F97316"
LARANJA_ESCURO = "#C2410C"
LARANJA_CLARO = "#FDBA74"
LARANJA_SUAVE = "#FFF7ED"
CINZA = "#64748B"
FUNDO = "#F8FAFC"


# ============================================================
# CSS
# ============================================================

st.markdown("""
<style>

    /* Fundo geral */
    .stApp {
        background-color: #F8FAFC;
    }

    /* Remove espaço excessivo superior */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    /* Título */
    .dashboard-title {
        font-size: 34px;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0px;
    }

    .dashboard-subtitle {
        color: #64748B;
        font-size: 15px;
        margin-bottom: 25px;
    }

    /* Cards KPI */
    .kpi-card {
        background: white;
        border-radius: 14px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        min-height: 125px;
    }

    .kpi-title {
        font-size: 13px;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #1E293B;
        margin-top: 8px;
    }

    .kpi-accent {
        width: 40px;
        height: 4px;
        background: #F97316;
        border-radius: 5px;
        margin-top: 12px;
    }

    /* Cabeçalhos */
    h1, h2, h3 {
        color: #1E293B;
    }

    /* Botões */
    .stButton > button {
        background-color: #F97316;
        color: white;
        border: none;
        border-radius: 8px;
    }

    .stButton > button:hover {
        background-color: #C2410C;
        color: white;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# CARREGAMENTO
# ============================================================

@st.cache_data
def carregar_dados():

    caminho = Path(ARQUIVO)

    if not caminho.exists():
        return None

    df = pd.read_csv(caminho)

    # Normalizar nomes
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Data
    if "data_venda" in df.columns:

        df["data_venda"] = pd.to_datetime(
            df["data_venda"],
            errors="coerce"
        )

        df["ano"] = df["data_venda"].dt.year
        df["mes"] = df["data_venda"].dt.month

    # Valor
    if "valor_total" in df.columns:

        df["valor_total"] = pd.to_numeric(
            df["valor_total"],
            errors="coerce"
        ).fillna(0)

    return df


df = carregar_dados()


# ============================================================
# CABEÇALHO
# ============================================================

st.markdown(
    '<div class="dashboard-title">Dashboard de Vendas</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Visão executiva • Performance comercial e análise de vendas'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# VALIDAR ARQUIVO
# ============================================================

if df is None:

    st.error(
        f"Arquivo {ARQUIVO} não encontrado."
    )

    st.stop()


if "valor_total" not in df.columns:

    st.error(
        "O CSV precisa possuir a coluna valor_total."
    )

    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown("## 🟠 Filtros")

df_filtrado = df.copy()


# ------------------------
# ANO
# ------------------------

if "ano" in df.columns:

    anos = sorted(
        df["ano"]
        .dropna()
        .unique()
    )

    ano_selecionado = st.sidebar.multiselect(
        "Ano",
        anos,
        default=anos
    )

    if ano_selecionado:

        df_filtrado = df_filtrado[
            df_filtrado["ano"].isin(
                ano_selecionado
            )
        ]


# ------------------------
# CATEGORIA
# ------------------------

if "categoria" in df.columns:

    categorias = sorted(
        df["categoria"]
        .dropna()
        .unique()
    )

    categoria_selecionada = st.sidebar.multiselect(
        "Categoria",
        categorias,
        default=categorias
    )

    if categoria_selecionada:

        df_filtrado = df_filtrado[
            df_filtrado["categoria"].isin(
                categoria_selecionada
            )
        ]


# ------------------------
# ESTADO
# ------------------------

if "estado" in df.columns:

    estados = sorted(
        df["estado"]
        .dropna()
        .unique()
    )

    estado_selecionado = st.sidebar.multiselect(
        "Estado",
        estados,
        default=estados
    )

    if estado_selecionado:

        df_filtrado = df_filtrado[
            df_filtrado["estado"].isin(
                estado_selecionado
            )
        ]


# ------------------------
# CANAL
# ------------------------

if "canal" in df.columns:

    canais = sorted(
        df["canal"]
        .dropna()
        .unique()
    )

    canal_selecionado = st.sidebar.multiselect(
        "Canal",
        canais,
        default=canais
    )

    if canal_selecionado:

        df_filtrado = df_filtrado[
            df_filtrado["canal"].isin(
                canal_selecionado
            )
        ]


# ============================================================
# KPIs
# ============================================================

total_vendas = df_filtrado["valor_total"].sum()

numero_vendas = len(df_filtrado)

ticket_medio = (
    total_vendas / numero_vendas
    if numero_vendas > 0
    else 0
)

quantidade = (
    df_filtrado["quantidade"].sum()
    if "quantidade" in df_filtrado.columns
    else numero_vendas
)


def moeda(valor):

    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )


def card(titulo, valor):

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-title">
                {titulo}
            </div>

            <div class="kpi-value">
                {valor}
            </div>

            <div class="kpi-accent"></div>

        </div>
        """,
        unsafe_allow_html=True
    )


c1, c2, c3, c4 = st.columns(4)

with c1:
    card(
        "Faturamento",
        moeda(total_vendas)
    )

with c2:
    card(
        "Vendas",
        f"{numero_vendas:,}".replace(",", ".")
    )

with c3:
    card(
        "Ticket Médio",
        moeda(ticket_medio)
    )

with c4:
    card(
        "Itens Vendidos",
        f"{quantidade:,.0f}".replace(",", ".")
    )


st.write("")


# ============================================================
# CONFIGURAÇÃO DOS GRÁFICOS
# ============================================================

def configurar_grafico(fig):

    fig.update_layout(

        plot_bgcolor="white",
        paper_bgcolor="white",

        font=dict(
            family="Arial",
            color="#475569"
        ),

        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20
        ),

        title_font=dict(
            size=17,
            color="#1E293B"
        ),

        hoverlabel=dict(
            bgcolor="white",
            font_size=13
        )
    )

    fig.update_xaxes(
        showgrid=False
    )

    fig.update_yaxes(
        gridcolor="#F1F5F9"
    )

    return fig


# ============================================================
# VENDAS POR ANO
# ============================================================

col1, col2 = st.columns([2, 1])


with col1:

    if "ano" in df_filtrado.columns:

        vendas_ano = (
            df_filtrado
            .groupby("ano", as_index=False)
            ["valor_total"]
            .sum()
        )

        fig_ano = px.bar(
            vendas_ano,
            x="ano",
            y="valor_total",
            title="Faturamento por Ano",
            labels={
                "ano": "Ano",
                "valor_total": "Faturamento"
            }
        )

        fig_ano.update_traces(
            marker_color=LARANJA,
            marker_line_width=0,
            hovertemplate=(
                "<b>Ano %{x}</b><br>"
                "R$ %{y:,.2f}"
                "<extra></extra>"
            )
        )

        configurar_grafico(fig_ano)

        st.plotly_chart(
            fig_ano,
            use_container_width=True
        )


# ============================================================
# CATEGORIAS
# ============================================================

with col2:

    if "categoria" in df_filtrado.columns:

        vendas_categoria = (
            df_filtrado
            .groupby(
                "categoria",
                as_index=False
            )
            ["valor_total"]
            .sum()
            .sort_values(
                "valor_total",
                ascending=False
            )
        )

        fig_categoria = px.pie(
            vendas_categoria,
            names="categoria",
            values="valor_total",
            title="Participação por Categoria",
            hole=0.65,
            color_discrete_sequence=[
                "#C2410C",
                "#EA580C",
                "#F97316",
                "#FB923C",
                "#FDBA74",
                "#FED7AA",
                "#FFEDD5",
                "#FFF7ED"
            ]
        )

        fig_categoria.update_traces(
            textposition="outside",
            textinfo="percent",
            hovertemplate=(
                "<b>%{label}</b><br>"
                "R$ %{value:,.2f}<br>"
                "%{percent}"
                "<extra></extra>"
            )
        )

        configurar_grafico(
            fig_categoria
        )

        st.plotly_chart(
            fig_categoria,
            use_container_width=True
        )


# ============================================================
# EVOLUÇÃO DAS VENDAS
# ============================================================

if "data_venda" in df_filtrado.columns:

    vendas_mes = (
        df_filtrado
        .dropna(
            subset=["data_venda"]
        )
        .set_index("data_venda")
        .resample("ME")
        ["valor_total"]
        .sum()
        .reset_index()
    )

    fig_linha = px.line(
        vendas_mes,
        x="data_venda",
        y="valor_total",
        title="Evolução do Faturamento",
        labels={
            "data_venda": "",
            "valor_total": "Faturamento"
        }
    )

    fig_linha.update_traces(

        line=dict(
            color=LARANJA,
            width=3
        ),

        mode="lines",

        fill="tozeroy",

        fillcolor="rgba(249,115,22,0.08)",

        hovertemplate=(
            "<b>%{x|%m/%Y}</b><br>"
            "R$ %{y:,.2f}"
            "<extra></extra>"
        )
    )

    configurar_grafico(
        fig_linha
    )

    st.plotly_chart(
        fig_linha,
        use_container_width=True
    )


# ============================================================
# ESTADO E CANAL
# ============================================================

c1, c2 = st.columns(2)


with c1:

    if "estado" in df_filtrado.columns:

        estado = (
            df_filtrado
            .groupby(
                "estado",
                as_index=False
            )
            ["valor_total"]
            .sum()
            .sort_values(
                "valor_total",
                ascending=True
            )
        )

        fig_estado = px.bar(
            estado,
            x="valor_total",
            y="estado",
            orientation="h",
            title="Faturamento por Estado"
        )

        fig_estado.update_traces(
            marker_color=LARANJA
        )

        configurar_grafico(
            fig_estado
        )

        st.plotly_chart(
            fig_estado,
            use_container_width=True
        )


with c2:

    if "canal" in df_filtrado.columns:

        canal = (
            df_filtrado
            .groupby(
                "canal",
                as_index=False
            )
            ["valor_total"]
            .sum()
            .sort_values(
                "valor_total",
                ascending=False
            )
        )

        fig_canal = px.bar(
            canal,
            x="canal",
            y="valor_total",
            title="Faturamento por Canal"
        )

        fig_canal.update_traces(
            marker_color=LARANJA_ESCURO
        )

        configurar_grafico(
            fig_canal
        )

        st.plotly_chart(
            fig_canal,
            use_container_width=True
        )


# ============================================================
# DETALHAMENTO
# ============================================================

st.markdown("### Detalhamento das Vendas")

st.caption(
    f"{len(df_filtrado):,} registros encontrados"
    .replace(",", ".")
)

st.dataframe(
    df_filtrado,
    use_container_width=True,
    hide_index=True,
    height=450
)


# ============================================================
# DOWNLOAD
# ============================================================

csv = df_filtrado.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇ Baixar dados filtrados",
    data=csv,
    file_name="vendas_filtradas.csv",
    mime="text/csv"
)
import sys
sys.exit()
from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# CONFIGURAÇÃO DA PÁGINA
# --------------------------------------------------

st.set_page_config(
    page_title="Dashboard de Vendas",
    layout="wide"
)

st.title("📊 Dashboard de Vendas")


# --------------------------------------------------
# CARREGAR CSV
# --------------------------------------------------

# Caminho relativo ao script (funciona em qualquer pasta)
arquivo = Path(__file__).parent / "vendas.csv"


@st.cache_data
def carregar_dados(caminho):
    return pd.read_csv(caminho)


df = carregar_dados(arquivo).copy()


# --------------------------------------------------
# TRATAR DATA
# --------------------------------------------------

df["DataVenda"] = pd.to_datetime(df["DataVenda"], errors="coerce")
df["ValorVenda"] = pd.to_numeric(df["ValorVenda"], errors="coerce")
df = df.dropna(subset=["DataVenda", "ValorVenda"])

# Cria o ano automaticamente a partir da data
df["Ano"] = df["DataVenda"].dt.year


# --------------------------------------------------
# INDICADORES
# --------------------------------------------------

def formatar_brl(valor):
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


total_vendas = df["ValorVenda"].sum()
quantidade = len(df)

col1, col2 = st.columns(2)

col1.metric(
    "Total de Vendas",
    formatar_brl(total_vendas)
)

col2.metric(
    "Quantidade de Vendas",
    f"{quantidade:,}".replace(",", ".")
)


# --------------------------------------------------
# VENDAS POR ANO
# --------------------------------------------------

vendas_ano = (
    df.groupby("Ano", as_index=False)["ValorVenda"]
      .sum()
)
# Ano como texto para o eixo não mostrar valores como 2024.5
vendas_ano["Ano"] = vendas_ano["Ano"].astype(str)


# --------------------------------------------------
# GRÁFICO
# --------------------------------------------------

st.subheader("Vendas por Ano")

fig = px.bar(
    vendas_ano,
    x="Ano",
    y="ValorVenda",
    text_auto=".2s",
    labels={
        "Ano": "Ano",
        "ValorVenda": "Valor de Vendas"
    }
)
fig.update_xaxes(type="category")

st.plotly_chart(
    fig,
    width="stretch"
)


# --------------------------------------------------
# TABELA DETALHADA
# --------------------------------------------------

st.subheader("Detalhamento das Vendas")

st.dataframe(
    df,
    width="stretch",
    hide_index=True,
    column_config={
        "DataVenda": st.column_config.DateColumn("Data da Venda", format="DD/MM/YYYY"),
        "ValorVenda": st.column_config.NumberColumn("Valor da Venda", format="R$ %.2f"),
        "Ano": st.column_config.NumberColumn("Ano", format="%d"),
    }
)
