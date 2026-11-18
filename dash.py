import hmac

import streamlit as st
from databricks import sql

st.set_page_config(page_title="Alunos", page_icon="🎓", layout="wide")

COLUNAS = [
    "codigo", "familiaid", "nombres", "apepaterno",
    "apematerno", "tipodocumento", "numerodocumento",
]

st.title("🎓 Alunos")

# O app está hospedado em uma URL pública: não consultar nem exibir dados
# pessoais antes de verificar a senha configurada em Secrets.
if "APP_PASSWORD" not in st.secrets:
    st.error("Configure APP_PASSWORD em Settings > Secrets antes de usar este dashboard.")
    st.stop()

senha = st.text_input("Senha de acesso", type="password")
if not senha:
    st.stop()
if not hmac.compare_digest(senha, str(st.secrets["APP_PASSWORD"])):
    st.error("Senha incorreta.")
    st.stop()

@st.cache_data(ttl=3600, show_spinner="Consultando Databricks...")
def carregar_alunos():
    with sql.connect(
        server_hostname=st.secrets["DATABRICKS_SERVER_HOSTNAME"],
        http_path=st.secrets["DATABRICKS_HTTP_PATH"],
        access_token=st.secrets["DATABRICKS_TOKEN"],
    ) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT codigo, familiaid, nombres, apepaterno,
                       apematerno, tipodocumento, numerodocumento
                FROM workspace.silver.alumnos
            """)
            linhas = cursor.fetchall()
            import pandas as pd
            return pd.DataFrame.from_records(linhas, columns=COLUNAS)

try:
    df = carregar_alunos()
except Exception:
    st.error("Não foi possível consultar o Databricks. Consulte os logs privados do aplicativo para diagnosticar a conexão.")
    raise

st.dataframe(df, use_container_width=True, hide_index=True)
