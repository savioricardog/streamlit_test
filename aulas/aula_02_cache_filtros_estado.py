"""
==============================================================================
FIESC / SENAI - Visualização de Dados e BI (Módulo 2 • Semana 11)
AULA 02: Interatividade Dinâmica, Filtros Cruzados e Cache Avançado
==============================================================================
Conceitos trabalhados nesta aula:
1. Gargalo do ciclo de reexecução (Rerun Model) ao conectar com bancos
2. Otimização com @st.cache_data (ttl e show_spinner)
3. Diferença de @st.cache_resource (conexões persistentes)
4. Filtros reativos cruzados na sidebar (multiselect e date_input)
5. Gerenciamento de estado com st.session_state e callbacks
==============================================================================
"""

import streamlit as st
import pandas as pd
import os
import toml
from datetime import timedelta

# Localizador dinâmico do CSV e secrets (funciona rodando da raiz ou de dentro da pasta aulas/)
DIRETORIO_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_CSV = os.path.join(DIRETORIO_PROJETO, "dados_b3_reais.csv")
if not os.path.exists(CAMINHO_CSV):
    CAMINHO_CSV = "dados_b3_reais.csv"

# Carrega credenciais do .streamlit/secrets.toml da raiz se não estiver no contexto local
caminho_secrets = os.path.join(DIRETORIO_PROJETO, ".streamlit", "secrets.toml")
db_kwargs = {}
if os.path.exists(caminho_secrets):
    try:
        sec = toml.load(caminho_secrets)
        db_kwargs = sec.get("connections", {}).get("postgresql", {})
    except Exception:
        pass

st.set_page_config(page_title="Aula 02 - Cache e Estado", page_icon="⚡", layout="wide")

st.title("⚡ Aula 02: Caching Avançado, Filtros Cruzados & Estado")

# ------------------------------------------------------------------------------
# 1. GERENCIAMENTO DE MEMÓRIA COM CACHE (Slides 21 a 25)
# ------------------------------------------------------------------------------
# @st.cache_resource: mantem a mesma conexao viva para todos os usuarios (Slide 22)
@st.cache_resource
def obter_conexao():
    if db_kwargs:
        return st.connection("postgresql", type="sql", **db_kwargs)
    return st.connection("postgresql", type="sql")

# @st.cache_data: guarda copia dos dados na memoria por 10 minutos (Slide 21 e 24)
@st.cache_data(ttl=600, show_spinner="Carregando base de ações do banco...")
def carregar_dados_com_cache():
    try:
        conn = obter_conexao()
        df = conn.query("SELECT data, preco_fechamento, volume, ticker FROM acoes_b3 ORDER BY data ASC;")
    except Exception:
        df = pd.read_csv(CAMINHO_CSV)
    
    df["data"] = pd.to_datetime(df["data"]).dt.date
    df["preco_fechamento"] = pd.to_numeric(df["preco_fechamento"], errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    return df.dropna().sort_values(by=["ticker", "data"]).reset_index(drop=True)

df_bruto = carregar_dados_com_cache()
todos_tickers = sorted(df_bruto["ticker"].unique().tolist())
data_min = df_bruto["data"].min()
data_max = df_bruto["data"].max()

# ------------------------------------------------------------------------------
# 2. PERSISTÊNCIA DE ESTADO COM st.session_state & CALLBACKS (Slides 27 a 29)
# ------------------------------------------------------------------------------
tickers_iniciais = [t for t in ["PETR4", "VALE3", "ITUB4"] if t in todos_tickers]
periodo_inicial = (max(data_min, data_max - timedelta(days=365)), data_max)

if "sel_tickers" not in st.session_state:
    st.session_state.sel_tickers = tickers_iniciais

if "sel_periodo" not in st.session_state:
    st.session_state.sel_periodo = periodo_inicial

def callback_reset():
    """Função Callback disparada pelo botão (Slide 29)"""
    st.session_state.sel_tickers = tickers_iniciais
    st.session_state.sel_periodo = periodo_inicial

# ------------------------------------------------------------------------------
# 3. FILTROS REATIVOS CRUZADOS NA SIDEBAR (Slide 19)
# ------------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Filtros Reativos")
    
    tickers_escolhidos = st.multiselect(
        "Selecione as Ações:",
        options=todos_tickers,
        key="sel_tickers"
    )
    
    periodo_escolhido = st.date_input(
        "Período de Análise:",
        min_value=data_min,
        max_value=data_max,
        key="sel_periodo"
    )
    
    # Botão de reset com callback
    st.button("🔄 Resetar Filtros", on_click=callback_reset, use_container_width=True)

# ------------------------------------------------------------------------------
# 4. APLICAÇÃO DOS FILTROS CRUZADOS NO PANDAS (Slide 19)
# ------------------------------------------------------------------------------
if not tickers_escolhidos:
    st.warning("Selecione pelo menos uma ação para visualizar os dados.")
    st.stop()

if isinstance(periodo_escolhido, (tuple, list)) and len(periodo_escolhido) == 2:
    dt_ini, dt_fim = periodo_escolhido
else:
    dt_ini, dt_fim = periodo_inicial

df_filtrado = df_bruto[
    (df_bruto["ticker"].isin(tickers_escolhidos)) &
    (df_bruto["data"] >= dt_ini) &
    (df_bruto["data"] <= dt_fim)
]

st.markdown(f"**Registros filtrados em memória:** {len(df_filtrado):,} linhas.")
st.dataframe(df_filtrado, use_container_width=True, height=400)
