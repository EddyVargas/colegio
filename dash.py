
import streamlit as st
import pandas as pd
import plotly.express as px
from databricks import sql

st.set_page_config(
    page_title="Dashboard de Alunos",
    page_icon="🎓",
    layout="wide"
)

LARANJA = "#F97316"
LARANJA_ESCURO = "#C2410C"

COLUNAS = [
    "codigo",
    "familiaid",
    "nombres",
    "apepaterno",
    "apematerno",
    "tipodocumento",
    "numerodocumento",
]

st.title("🎓 Dashboard de Alunos")
st.caption("Dados do Databricks | workspace.silver.alumnos")


# ==========================================
# CARREGAR DADOS
# ==========================================

@st.cache_data(
    ttl=3600,
    show_spinner="Consultando Databricks..."
)
def carregar_alunos():

    with sql.connect(
        server_hostname=st.secrets["DATABRICKS_SERVER_HOSTNAME"],
        http_path=st.secrets["DATABRICKS_HTTP_PATH"],
        access_token=st.secrets["DATABRICKS_TOKEN"],
    ) as conexao:

        with conexao.cursor() as cursor:

            cursor.execute("""
                SELECT
                    codigo,
                    familiaid,
                    nombres,
                    apepaterno,
                    apematerno,
                    tipodocumento,
                    numerodocumento
                FROM workspace.silver.alumnos
            """)

            linhas = cursor.fetchall()

    return pd.DataFrame.from_records(
        linhas,
        columns=COLUNAS
    )


try:
    df = carregar_alunos()

except Exception:
    st.error(
        "Não foi possível consultar o Databricks. "
        "Verifique a conexão e as credenciais."
    )
    st.stop()


# ==========================================
# INDICADORES
# ==========================================

total_alunos = len(df)
total_familias = df["familiaid"].nunique()

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Total de Alunos",
        f"{total_alunos:,}".replace(",", ".")
    )

with col2:
    st.metric(
        "Total de Famílias",
        f"{total_familias:,}".replace(",", ".")
    )


st.divider()


# ==========================================
# GRÁFICO 1 - TIPO DE DOCUMENTO
# ==========================================

documentos = (
    df.assign(
        tipodocumento=df["tipodocumento"]
        .fillna("Não informado")
        .astype(str)
    )
    .groupby("tipodocumento", as_index=False)
    .size()
    .rename(columns={"size": "quantidade"})
    .sort_values("quantidade", ascending=False)
)

fig_documentos = px.bar(
    documentos,
    x="tipodocumento",
    y="quantidade",
    title="Alunos por Tipo de Documento",
    text="quantidade",
    labels={
        "tipodocumento": "Tipo de Documento",
        "quantidade": "Quantidade de Alunos"
    }
)

fig_documentos.update_traces(
    marker_color=LARANJA,
    textposition="outside"
)

fig_documentos.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    yaxis=dict(rangemode="tozero")
)


# ==========================================
# GRÁFICO 2 - ALUNOS POR FAMÍLIA
# ==========================================

familias = (
    df.dropna(subset=["familiaid"])
    .assign(
        familiaid=lambda dados:
        dados["familiaid"].astype(str)
    )
    .groupby("familiaid", as_index=False)
    .size()
    .rename(columns={"size": "quantidade"})
    .sort_values(
        ["quantidade", "familiaid"],
        ascending=[False, True]
    )
    .head(10)
)

fig_familias = px.bar(
    familias,
    x="familiaid",
    y="quantidade",
    title="Top 10 Famílias por Quantidade de Alunos",
    text="quantidade",
    labels={
        "familiaid": "Código da Família",
        "quantidade": "Quantidade de Alunos"
    }
)

fig_familias.update_traces(
    marker_color=LARANJA_ESCURO,
    textposition="outside"
)

fig_familias.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis=dict(type="category"),
    yaxis=dict(rangemode="tozero")
)


# ==========================================
# EXIBIR OS DOIS GRÁFICOS
# ==========================================

grafico1, grafico2 = st.columns(2)

with grafico1:
    st.plotly_chart(
        fig_documentos,
        use_container_width=True
    )

with grafico2:
    st.plotly_chart(
        fig_familias,
        use_container_width=True
    )


# ==========================================
# TABELA DE ALUNOS
# ==========================================

st.divider()

st.subheader("Detalhamento dos Alunos")

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    height=450
)
