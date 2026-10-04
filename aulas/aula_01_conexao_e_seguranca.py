"""
==============================================================================
FIESC / SENAI - Visualização de Dados e BI (Módulo 2 • Semana 11)
AULA 01: Conexão a Dados, Pandas e Segurança com secrets.toml
==============================================================================
Conceitos trabalhados nesta aula:
1. Conexão nativa com st.connection("postgresql", type="sql")
2. Isolamento de credenciais seguras no .streamlit/secrets.toml (ignorado no Git)
3. Fallback resiliente com try/except para arquivo CSV local
4. Consulta SQL dinâmica parametrizada com :param e params={} (Slide 15)
==============================================================================
"""

import os
import streamlit as st
import pandas as pd

# Localizador dinâmico do CSV (funciona rodando da raiz ou de dentro da pasta aulas/)
DIRETORIO_PROJETO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMINHO_CSV = os.path.join(DIRETORIO_PROJETO, "dados_b3_reais.csv")
if not os.path.exists(CAMINHO_CSV):
    CAMINHO_CSV = "dados_b3_reais.csv"

st.set_page_config(page_title="Aula 01 - Conexão e Segurança", page_icon="🔒", layout="wide")

st.title("🔒 Aula 01: Conexão com PostgreSQL & Segurança")
st.markdown("Demonstração da conexão com o banco relacional na nuvem e resiliência.")

# ------------------------------------------------------------------------------
# 1. CONEXÃO COM FALLBACK RESILIENTE (Slide 13)
# ------------------------------------------------------------------------------
origem = "Supabase (PostgreSQL Cloud)"
try:
    # Obtém conexão usando as credenciais do .streamlit/secrets.toml
    conn = st.connection("postgresql", type="sql")
    
    # Teste de conexão simples
    df_teste = conn.query("SELECT DISTINCT ticker FROM acoes_b3 ORDER BY ticker ASC;", ttl=0)
    lista_tickers = df_teste["ticker"].tolist()
    st.success("🟢 Conexão com o Supabase estabelecida com sucesso!")
except Exception as erro:
    origem = "Fallback Local (dados_b3_reais.csv)"
    st.warning(f"🟡 Falha na conexão com o banco. Carregando contingência em CSV... Detalhe: {erro}")
    df_local = pd.read_csv(CAMINHO_CSV)
    lista_tickers = sorted(df_local["ticker"].unique().tolist())

# ------------------------------------------------------------------------------
# 2. PRÁTICA GUIADA: CONSULTA DINÂMICA PARAMETRIZADA (Slide 15)
# ------------------------------------------------------------------------------
st.markdown("---")
st.subheader("🔬 Prática do Slide 15: Consulta SQL Parametrizada")

col1, col2 = st.columns([1, 2])

with col1:
    ticker_selecionado = st.selectbox("Selecione o Ticker da Ação:", options=lista_tickers)
    limite = st.slider("Qtd. Registros:", 5, 20, 10)
    btn_consultar = st.button("Executar Consulta SQL")

with col2:
    st.code(f"""# Sintaxe ensinada no Slide 15:
query = "SELECT data, preco_fechamento, volume FROM acoes_b3 WHERE ticker = :ticker ORDER BY data DESC LIMIT :limite;"
df = conn.query(query, params={{"ticker": "{ticker_selecionado}", "limite": {limite}}})""", language="python")

if btn_consultar:
    try:
        if "Supabase" in origem:
            query = "SELECT data, preco_fechamento, volume, ticker FROM acoes_b3 WHERE ticker = :ticker ORDER BY data DESC LIMIT :limite;"
            df_resultado = conn.query(query, params={"ticker": ticker_selecionado, "limite": limite})
        else:
            # Fallback para o CSV
            df_resultado = df_local[df_local["ticker"] == ticker_selecionado].sort_values(by="data", ascending=False).head(limite)

        # Exibição do Cartão de KPI e Tabela (Slide 15, Passo 3)
        preco_ultimo = df_resultado["preco_fechamento"].iloc[0]
        st.metric(label=f"Última Cotação de {ticker_selecionado}", value=f"R$ {preco_ultimo:.2f}")
        st.dataframe(df_resultado, use_container_width=True)
    except Exception as e:
        st.error(f"Erro na execução da consulta: {e}")
