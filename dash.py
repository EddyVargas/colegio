
import streamlit as st
from databricks import sql

st.set_page_config(page_title="Teste Databricks", layout="wide")

st.title("Teste de conexão Databricks")

if st.button("Testar conexão"):
    try:
        with st.spinner("Conectando ao SQL Warehouse..."):
            with sql.connect(
                server_hostname=st.secrets["DATABRICKS_SERVER_HOSTNAME"],
                http_path=st.secrets["DATABRICKS_HTTP_PATH"],
                access_token=st.secrets["DATABRICKS_TOKEN"],
            ) as conexao:
                with conexao.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    resultado = cursor.fetchone()

        st.success(f"Conexão realizada! Resultado: {resultado[0]}")

    except Exception as erro:
        st.error("Falha ao conectar ao Databricks.")
        st.write("Tipo do erro:", type(erro).__name__)
        st.info(
            "Consulte os logs privados do Streamlit para "
            "identificar a mensagem original."
        )
        print(
            f"Falha Databricks: {type(erro).__name__}: {erro}",
            flush=True
        )
