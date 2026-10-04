"""
==============================================================================
FIESC / SENAI - Visualização de Dados e BI (Módulo 2 • Semana 11)
AULA 03: Visualizações Interativas com Plotly, KPIs e Deploy na Nuvem
==============================================================================
Conceitos trabalhados nesta aula:
1. Indicadores de KPI executivos com st.columns e st.metric (Slide 39)
2. Visualização dinâmica interativa com Plotly (Linhas, Base 100 e Volume)
3. Formatação moderna de tabelas com column_config e download em CSV
4. Estruturação do requirements.txt e deploy no Streamlit Community Cloud
==============================================================================
"""

import streamlit as st
import os
import pandas as pd
import plotly.express as px
from datetime import timedelta, date

# Localizador dinâmico do CSV (funciona rodando da raiz ou de dentro da pasta aulas/)
DIRETORIO_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_CSV = os.path.join(DIRETORIO_PROJETO, "dados_b3_reais.csv")
if not os.path.exists(CAMINHO_CSV):
    CAMINHO_CSV = "dados_b3_reais.csv"

st.set_page_config(page_title="Aula 03 - Dashboard Final", page_icon="📈", layout="wide")

# ------------------------------------------------------------------------------
# 1. CARGA RESILIENTE E CACHEADA (Aulas 1 e 2)
# ------------------------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner="Carregando dados...")
def carregar_dados():
    try:
        conn = st.connection("postgresql", type="sql")
        df = conn.query("SELECT data, preco_fechamento, volume, ticker FROM acoes_b3 ORDER BY data ASC;")
    except Exception:
        df = pd.read_csv(CAMINHO_CSV)
    
    df["data"] = pd.to_datetime(df["data"]).dt.date
    df["preco_fechamento"] = pd.to_numeric(df["preco_fechamento"], errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    return df.dropna().sort_values(by=["ticker", "data"]).reset_index(drop=True)

df_bruto = carregar_dados()
todos_tickers = sorted(df_bruto["ticker"].unique().tolist())
data_min = df_bruto["data"].min()
data_max = df_bruto["data"].max()

# ------------------------------------------------------------------------------
# 2. ESTADO E FILTROS REATIVOS (Aula 2)
# ------------------------------------------------------------------------------
padrao_tickers = [t for t in ["PETR4", "VALE3", "ITUB4", "WEGE3"] if t in todos_tickers]
padrao_periodo = (max(data_min, data_max - timedelta(days=365 * 3)), data_max)

if "f_tickers" not in st.session_state:
    st.session_state.f_tickers = padrao_tickers
if "f_periodo" not in st.session_state:
    st.session_state.f_periodo = padrao_periodo

def resetar():
    st.session_state.f_tickers = padrao_tickers
    st.session_state.f_periodo = padrao_periodo

with st.sidebar:
    st.header("⚙️ Filtros")
    sel_tickers = st.multiselect("Ativos:", options=todos_tickers, key="f_tickers")
    sel_datas = st.date_input("Período:", min_value=data_min, max_value=data_max, key="f_periodo")
    
    st.markdown("### Visualização")
    modo_base100 = st.toggle("Comparar Retorno (Base 100)", value=False)
    escala_log = st.toggle("Escala Logarítmica", value=False)
    
    st.button("🔄 Resetar", on_click=resetar, use_container_width=True)

if not sel_tickers:
    st.warning("Selecione um ticker na barra lateral.")
    st.stop()

dt_ini, dt_fim = sel_datas if isinstance(sel_datas, (tuple, list)) and len(sel_datas) == 2 else padrao_periodo

df_filtrado = df_bruto[
    (df_bruto["ticker"].isin(sel_tickers)) &
    (df_bruto["data"] >= dt_ini) &
    (df_bruto["data"] <= dt_fim)
]

# ------------------------------------------------------------------------------
# 3. CABEÇALHO E CARTÕES DE KPI (Slide 39 - Requisito 4)
# ------------------------------------------------------------------------------
st.title("📊 Dashboard Executivo de Ações B3")

col1, col2, col3, col4 = st.columns(4)
vol_tot = df_filtrado["volume"].sum()
col1.metric("Volume Negociado", f"{vol_tot/1e6:.1f} M" if vol_tot >= 1e6 else f"{vol_tot:,.0f}")
col2.metric("Preço Médio", f"R$ {df_filtrado['preco_fechamento'].mean():.2f}")
col3.metric("Cotação Máxima", f"R$ {df_filtrado['preco_fechamento'].max():.2f}")
col4.metric("Cotação Mínima", f"R$ {df_filtrado['preco_fechamento'].min():.2f}")

st.markdown("---")

# ------------------------------------------------------------------------------
# 4. VISUALIZAÇÃO INTERATIVA COM PLOTLY (Slide 39 - Requisito 4)
# ------------------------------------------------------------------------------
tab1, tab2 = st.tabs(["📈 Gráficos Interativos", "📋 Tabela de Dados"])

with tab1:
    if modo_base100:
        st.subheader("Desempenho Relativo Acumulado (Base 100)")
        df_norm = df_filtrado.copy()
        df_norm["base_100"] = df_norm.groupby("ticker")["preco_fechamento"].transform(lambda x: (x / x.iloc[0]) * 100)
        fig_p = px.line(df_norm, x="data", y="base_100", color="ticker", title="Rentabilidade Comparativa")
        fig_p.add_hline(y=100, line_dash="dash", line_color="gray")
    else:
        st.subheader("Histórico do Preço de Fechamento (R$)")
        fig_p = px.line(df_filtrado, x="data", y="preco_fechamento", color="ticker", log_y=escala_log)

    fig_p.update_layout(template="plotly_dark", hovermode="x unified")
    st.plotly_chart(fig_p, use_container_width=True)

    st.subheader("Volume de Negociação por Ativo")
    fig_v = px.bar(df_filtrado, x="data", y="volume", color="ticker", barmode="group")
    fig_v.update_layout(template="plotly_dark")
    st.plotly_chart(fig_v, use_container_width=True)

with tab2:
    st.dataframe(
        df_filtrado,
        column_config={
            "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "preco_fechamento": st.column_config.NumberColumn("Preço", format="R$ %.2f"),
            "volume": st.column_config.NumberColumn("Volume", format="%d")
        },
        use_container_width=True,
        hide_index=True
    )
    st.download_button("📥 Baixar CSV", data=df_filtrado.to_csv(index=False).encode("utf-8"), file_name=f"cotacoes_{date.today()}.csv")
