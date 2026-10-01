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
