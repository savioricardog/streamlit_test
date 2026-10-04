import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

# Configuração de segurança para exibição de dados
pd.set_option("styler.render.max_elements", 1_000_000)

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Dashboard Financeiro B3 | Análise Avançada",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização CSS refinada (Dark Mode Premium)
st.markdown("""
<style>
    /* Estilização dos cartões de métrica */
    div[data-testid="stMetric"] {
        background-color: #1A1F2C;
        border: 1px solid #2D3748;
        border-radius: 10px;
        padding: 16px 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    div[data-testid="stMetricLabel"] {
        color: #9CA3AF !important;
        font-weight: 500;
        font-size: 0.9rem;
    }
    div[data-testid="stMetricValue"] {
        color: #F3F4F6 !important;
        font-weight: 700;
        font-size: 1.6rem;
    }
    .badge-cloud {
        background-color: #064E3B;
        color: #34D399;
        border: 1px solid #059669;
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
    .badge-fallback {
        background-color: #78350F;
        color: #FCD34D;
        border: 1px solid #D97706;
        padding: 5px 12px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# AULA 1 & 2: CONEXÃO COM BANCO DE DADOS, FALLBACK E CACHE INTELIGENTE
# ==============================================================================
@st.cache_data(ttl=600, show_spinner="Consultando dados de mercado no Supabase...")
def _consultar_supabase():
    """
    Executa a query diretamente no Supabase.
    Se a conexão for bem-sucedida, o resultado é cacheado por 10 minutos.
    Se houver erro, a exceção é disparada e o Streamlit NÃO armazena o erro em cache!
    """
    conn = st.connection("postgresql", type="sql")
    query = "SELECT data, preco_fechamento, volume, ticker FROM acoes_b3 ORDER BY data ASC;"
    df = conn.query(query, ttl=600)
    
    if df is None or df.empty:
        raise ValueError("A consulta ao banco Supabase retornou vazia.")
        
    df["data"] = pd.to_datetime(df["data"]).dt.date
    df["preco_fechamento"] = pd.to_numeric(df["preco_fechamento"], errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
    df = df.dropna(subset=["preco_fechamento", "data"]).sort_values(by=["ticker", "data"]).reset_index(drop=True)
    return df

def carregar_dados():
    """
    Coordena a carga com resiliência: tenta o Supabase e, em caso de falha,
    aciona imediatamente o Fallback local sem contaminar a memória de cache.
    """
    try:
        df = _consultar_supabase()
        return df, "Supabase (PostgreSQL Cloud)", None
    except Exception as erro:
        df_local = pd.read_csv("dados_b3_reais.csv")
        df_local["data"] = pd.to_datetime(df_local["data"]).dt.date
        df_local["preco_fechamento"] = pd.to_numeric(df_local["preco_fechamento"], errors="coerce")
        df_local["volume"] = pd.to_numeric(df_local["volume"], errors="coerce")
        df_local = df_local.dropna(subset=["preco_fechamento", "data"]).sort_values(by=["ticker", "data"]).reset_index(drop=True)
        return df_local, "Fallback Local (dados_b3_reais.csv)", str(erro)


# Carga dos dados com cache ativo
df_bruto, origem_dados, erro_conexao = carregar_dados()

# Lista de todos os tickers disponíveis
todos_tickers = sorted(df_bruto["ticker"].unique().tolist())
data_minima = df_bruto["data"].min()
data_maxima = df_bruto["data"].max()

# Seleção inicial inteligente: 4 blue chips conhecidas para evitar "gráfico espaguete"
tickers_padrao_sugeridos = [t for t in ["PETR4", "VALE3", "ITUB4", "WEGE3"] if t in todos_tickers]
if not tickers_padrao_sugeridos:
    tickers_padrao_sugeridos = todos_tickers[:4]

# Data inicial padrão: últimos 3 anos (para evitar distorções de moedas antigas/lotes de mil dos anos 2000)
data_inicio_padrao = max(data_minima, data_maxima - timedelta(days=365 * 3))


# ==============================================================================
# AULA 2: PERSISTÊNCIA DE ESTADO (st.session_state) & CALLBACKS
# ==============================================================================
if "filtro_tickers" not in st.session_state:
    st.session_state.filtro_tickers = tickers_padrao_sugeridos

if "filtro_periodo" not in st.session_state:
    st.session_state.filtro_periodo = (data_inicio_padrao, data_maxima)

def resetar_filtros():
    """Callback para resetar filtros para o estado ideal de visualização"""
    st.session_state.filtro_tickers = tickers_padrao_sugeridos
    st.session_state.filtro_periodo = (data_inicio_padrao, data_maxima)


# ==============================================================================
# BARRA LATERAL: FILTROS REATIVOS CRUZADOS
# ==============================================================================
with st.sidebar:
    st.title("⚙️ Filtros do Mercado")
    
    # Status da conexão
    if "Supabase" in origem_dados:
        st.markdown(f'<span class="badge-cloud">🟢 {origem_dados}</span>', unsafe_allow_html=True)
        st.caption("Conectado ao vivo com o banco PostgreSQL no Supabase.")
    else:
        st.markdown(f'<span class="badge-fallback">🟡 {origem_dados}</span>', unsafe_allow_html=True)
        if erro_conexao:
            with st.expander("🔍 Motivo do Fallback (Diagnóstico):", expanded=True):
                st.caption("Erro retornado ao tentar conectar no Supabase:")
                st.code(erro_conexao, language="bash")
        st.caption("Configure as credenciais no secrets.toml ou no painel da nuvem.")

    st.markdown("---")
    
    # Filtro 1: Seleção de Ativos
    tickers_selecionados = st.multiselect(
        "Selecione os Ativos (Tickers):",
        options=todos_tickers,
        key="filtro_tickers",
        help="Dica: selecione de 1 a 5 ativos para uma visualização gráfica mais limpa."
    )
    
    # Filtro 2: Período de Análise
    periodo_selecionado = st.date_input(
        "Período de Análise:",
        min_value=data_minima,
        max_value=data_maxima,
        key="filtro_periodo",
        help="Selecione a data de início e fim."
    )
    
    st.markdown("### 🎛️ Visualização do Gráfico")
    
    # Filtro 3: Normalização Base 100
    modo_comparativo = st.toggle(
        "Comparar Retorno (Base 100)",
        value=False,
        help="Converte a cotação inicial de cada ação para 100 e compara a rentabilidade acumulada percentual."
    )
    
    # Filtro 4: Escala Logarítmica
    escala_log = st.toggle(
        "Escala Logarítmica (Eixo Y)",
        value=False,
        help="Útil para visualizar ações com preços muito diferentes (ex: R$ 5 vs R$ 10.000) sem distorcer o gráfico."
    )
    
    st.markdown("---")
    st.button("🔄 Restaurar Padrão Limpo", on_click=resetar_filtros, use_container_width=True)
    
    st.markdown("---")
    st.caption("FIESC / SENAI • Visualização de Dados e BI\nM2S11 - Streamlit Avançado")


# ==============================================================================
# APLICAÇÃO DOS FILTROS CRUZADOS NO DATAFRAME
# ==============================================================================
if not tickers_selecionados:
    st.warning("⚠️ Selecione pelo menos um ticker na barra lateral para visualizar o dashboard.")
    st.stop()

# Validação do intervalo de datas
if isinstance(periodo_selecionado, (tuple, list)) and len(periodo_selecionado) == 2:
    d_inicio, d_fim = periodo_selecionado
elif isinstance(periodo_selecionado, (tuple, list)) and len(periodo_selecionado) == 1:
    d_inicio = periodo_selecionado[0]
    d_fim = data_maxima
else:
    d_inicio, d_fim = data_inicio_padrao, data_maxima

# Filtragem encadeada
df_filtrado = df_bruto[
    (df_bruto["ticker"].isin(tickers_selecionados)) &
    (df_bruto["data"] >= d_inicio) &
    (df_bruto["data"] <= d_fim)
].copy()

if df_filtrado.empty:
    st.info("Nenhum dado encontrado para o período selecionado. Tente expandir o intervalo de datas.")
    st.stop()


# ==============================================================================
# CABEÇALHO E CARTÕES DE KPI
# ==============================================================================
st.title("📈 Performance de Ações B3")
st.markdown(
    f"Exibindo **{len(tickers_selecionados)} ativo(s)** ({', '.join(tickers_selecionados)}) "
    f"entre **{d_inicio.strftime('%d/%m/%Y')}** e **{d_fim.strftime('%d/%m/%Y')}**."
)

col1, col2, col3, col4 = st.columns(4)

volume_total = df_filtrado["volume"].sum()
preco_medio = df_filtrado["preco_fechamento"].mean()
maior_alta = df_filtrado["preco_fechamento"].max()
menor_baixa = df_filtrado["preco_fechamento"].min()

with col1:
    # Formatação de volume inteligente (Bilhões / Milhões / Milhares)
    if volume_total >= 1e9:
        vol_str = f"{volume_total / 1e9:.2f} B"
    elif volume_total >= 1e6:
        vol_str = f"{volume_total / 1e6:.1f} M"
    else:
        vol_str = f"{volume_total:,.0f}"
    st.metric(label="Volume Total Negociado", value=vol_str)

with col2:
    st.metric(label="Preço Médio no Período", value=f"R$ {preco_medio:,.2f}")

with col3:
    st.metric(label="Cotação Máxima", value=f"R$ {maior_alta:,.2f}")

with col4:
    st.metric(label="Cotação Mínima", value=f"R$ {menor_baixa:,.2f}")

st.markdown("---")


# ==============================================================================
# ABAS DE VISUALIZAÇÃO INTERATIVA
# ==============================================================================
tab_graficos, tab_tabela, tab_teoria = st.tabs([
    "📈 Análise Gráfica Interativa",
    "📋 Tabela de Dados & Exportação",
    "🎓 Conceitos Pedagógicos da Aula"
])

# Paleta de cores moderna e distinta
PALETA_CORES = ["#10B981", "#3B82F6", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#06B6D4", "#84CC16"]

with tab_graficos:
    # 1. GRÁFICO PRINCIPAL DE PREÇOS
    if modo_comparativo:
        st.markdown("### 🚀 Rentabilidade Relativa Normalizada (Base 100)")
        st.caption("Cada ativo inicia em 100 na primeira data do período. Valores acima de 100 indicam ganho percentual.")
        
        # Cria cópia ordenada para cálculo da base 100
        df_norm = df_filtrado.sort_values(by=["ticker", "data"]).copy()
        df_norm["base_100"] = df_norm.groupby("ticker")["preco_fechamento"].transform(
            lambda x: (x / x.iloc[0]) * 100 if x.iloc[0] > 0 else 100
        )
        
        fig_preco = px.line(
            df_norm,
            x="data",
            y="base_100",
            color="ticker",
            color_discrete_sequence=PALETA_CORES,
            labels={"base_100": "Desempenho (Base 100)", "data": "Data", "ticker": "Ativo"}
        )
        fig_preco.add_hline(y=100, line_dash="dash", line_color="#9CA3AF", annotation_text="Ponto de Entrada (100)")
        fig_preco.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>Data: %{x|%d/%m/%Y}<br>Desempenho: %{y:.2f} pts<extra></extra>",
            line=dict(width=2.5)
        )
        
    else:
        st.markdown("### 💰 Histórico do Preço de Fechamento (R$)")
        fig_preco = px.line(
            df_filtrado,
            x="data",
            y="preco_fechamento",
            color="ticker",
            color_discrete_sequence=PALETA_CORES,
            log_y=escala_log,
            labels={"preco_fechamento": "Cotação (R$)", "data": "Data", "ticker": "Ativo"}
        )
        fig_preco.update_traces(
            hovertemplate="<b>%{fullData.name}</b><br>Data: %{x|%d/%m/%Y}<br>Cotação: R$ %{y:,.2f}<extra></extra>",
            line=dict(width=2.5)
        )

    # Layout elegante: Legenda no topo sem sobreposição, grid suave
    fig_preco.update_layout(
        template="plotly_dark",
        hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(14,17,23,0.6)",
        margin=dict(l=10, r=10, t=30, b=10),
        height=480,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            title=None,
            font=dict(size=12)
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#1F2937",
            title=None
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#1F2937",
            title=None
        )
    )
    st.plotly_chart(fig_preco, use_container_width=True)

    # 2. GRÁFICO DE VOLUME / LIQUIDEZ
    st.markdown("### 📊 Volume de Negociação")
    fig_vol = px.bar(
        df_filtrado,
        x="data",
        y="volume",
        color="ticker",
        color_discrete_sequence=PALETA_CORES,
        barmode="group",
        labels={"volume": "Volume de Ações", "data": "Data", "ticker": "Ativo"}
    )
    fig_vol.update_traces(
        hovertemplate="<b>%{fullData.name}</b><br>Data: %{x|%d/%m/%Y}<br>Volume: %{y:,.0f}<extra></extra>"
    )
    fig_vol.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(14,17,23,0.6)",
        margin=dict(l=10, r=10, t=30, b=10),
        height=320,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5,
            title=None
        ),
        xaxis=dict(showgrid=True, gridcolor="#1F2937", title=None),
        yaxis=dict(showgrid=True, gridcolor="#1F2937", title=None)
    )
    st.plotly_chart(fig_vol, use_container_width=True)


with tab_tabela:
    st.subheader("Base de Cotações Filtrada")
    st.markdown("Consulte e baixe os dados resultantes dos filtros aplicados.")
    
    st.dataframe(
        df_filtrado,
        column_config={
            "data": st.column_config.DateColumn("Data", format="DD/MM/YYYY"),
            "preco_fechamento": st.column_config.NumberColumn("Preço Fechamento", format="R$ %.2f"),
            "volume": st.column_config.NumberColumn("Volume Negociado", format="%d"),
            "ticker": st.column_config.TextColumn("Ativo (Ticker)")
        },
        use_container_width=True,
        hide_index=True,
        height=420
    )
    
    csv_bytes = df_filtrado.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Baixar Dados Filtrados em CSV",
        data=csv_bytes,
        file_name=f"cotacoes_b3_filtradas_{date.today()}.csv",
        mime="text/csv",
        use_container_width=True
    )


with tab_teoria:
    st.subheader("Arquitetura e Recursos Avançados Utilizados")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        #### 1. Conexão & Resiliência
        * **`st.connection("postgresql", type="sql")`**: Conexão nativa e gerenciamento automático de conexões SQLAlchemy com o Supabase.
        * **Fallback com `try/except`**: Se o Supabase estiver indisponível ou as credenciais não existirem, o app reverte para o arquivo local `dados_b3_reais.csv`.
        * **Segurança**: Isolamento de credenciais no `.streamlit/secrets.toml` com bloqueio no `.gitignore`.
        """)
    with col_b:
        st.markdown("""
        #### 2. Caching & Performance
        * **`@st.cache_data(ttl=600)`**: Evita bater no banco de dados a cada clique do usuário. A consulta é reaproveitada da memória do servidor por 10 minutos.
        * **`st.session_state` e Callbacks**: Preserva as escolhas dos filtros no navegador e permite resetar parâmetros via `on_click=resetar_filtros`.
        * **Visualização Dinâmica**: Gráficos reativos gerados com **Plotly Express** integrados ao tema visual da aplicação.
        """)
