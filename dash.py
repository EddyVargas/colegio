import streamlit as st
import pandas as pd
import plotly.express as px
from databricks import sql

st.set_page_config(page_title="Dashboard de Matrículas", page_icon="🎓", layout="wide")
LARANJA = "#F97316"
st.markdown("""<style>
.stApp {background-color:#F8FAFC}
.block-container {padding-top:2rem}
h1,h2,h3 {color:#1E293B}
[data-testid="stMetric"] {background:white;border:1px solid #E2E8F0;border-radius:14px;padding:18px}
</style>""", unsafe_allow_html=True)

st.title("🎓 Dashboard de Matrículas")
st.caption("Dados atualizados diretamente do Databricks · workspace.bronze.matriculas")

@st.cache_data(ttl=3600, show_spinner="Consultando Databricks...")
def carregar_resumo():
    with sql.connect(
        server_hostname=st.secrets["DATABRICKS_SERVER_HOSTNAME"],
        http_path=st.secrets["DATABRICKS_HTTP_PATH"],
        access_token=st.secrets["DATABRICKS_TOKEN"],
    ) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) AS total_matriculas FROM workspace.bronze.matriculas")
            total = cursor.fetchone()[0]
            cursor.execute("DESCRIBE TABLE workspace.bronze.matriculas")
            colunas = [linha[0] for linha in cursor.fetchall() if linha[0] and not linha[0].startswith('#')]
    return int(total), colunas

if st.sidebar.button("🔄 Atualizar dados"):
    carregar_resumo.clear()
    st.rerun()

try:
    total, colunas = carregar_resumo()
except KeyError as erro:
    st.error(f"Credencial ausente nos Secrets: {erro}")
    st.info("Configure DATABRICKS_SERVER_HOSTNAME, DATABRICKS_HTTP_PATH e DATABRICKS_TOKEN nas configurações do app.")
    st.stop()
except Exception:
    st.error("Não foi possível consultar o Databricks. Confira o SQL Warehouse, as credenciais e as permissões da tabela.")
    st.stop()

c1, c2 = st.columns(2)
c1.metric("Total de matrículas", f"{total:,}".replace(",", "."))
c2.metric("Colunas disponíveis", len(colunas))

st.subheader("Conexão")
st.success("Databricks conectado. Consulta de matrículas concluída.")
st.caption("A contagem é armazenada em cache por até 1 hora. Use Atualizar dados para consultar novamente.")

# Por segurança, não exibimos registros individuais de alunos em um app público.
# Após confirmar o esquema, podem ser adicionados gráficos agregados por período ou situação.
st.info("Visualização agregada: os registros individuais de alunos não são exibidos neste aplicativo público.")
