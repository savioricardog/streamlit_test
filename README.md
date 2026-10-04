# 📈 Dashboard Financeiro B3 | Streamlit Avançado

Projeto prático desenvolvido para o curso de **Visualização de Dados e Business Intelligence (Módulo 2 - Semana 11)** da **FIESC / SENAI**.

Este projeto cobre de ponta a ponta as melhores práticas de desenvolvimento corporativo em Streamlit:
* **Aula 1:** Conexão nativa a banco de dados relacional (PostgreSQL na nuvem via **Supabase**), gestão segura de credenciais com `.streamlit/secrets.toml` e arquitetura resiliente com **Fallback Local em CSV**.
* **Aula 2:** Caching avançado (`@st.cache_data` com `ttl` e `show_spinner`), filtros reativos cruzados e persistência de estado com `st.session_state` e callbacks.
* **Aula 3:** KPIs executivos (`st.columns` e `st.metric`), gráficos interativos em **Plotly**, tabela de dados formatada e **Deploy em Produção no Streamlit Community Cloud**.

---

## 📁 Estrutura do Projeto

```text
├── .streamlit/
│   ├── config.toml           # Configurações de tema escuro e interface
│   ├── secrets.toml          # Suas credenciais do Supabase (NÃO versionado no Git)
│   └── secrets.toml.example  # Modelo para configuração das credenciais
├── .gitignore                # Proteção contra vazamento de credenciais e venv
├── dados_b3_reais.csv        # Base histórica real de cotações da B3 (1.500 registros)
├── schema_supabase.sql       # Script DDL para criar a tabela no Supabase
├── migrar_para_supabase.py   # Script Python opcional para carregar o CSV no Supabase
├── app.py                    # Aplicação principal (Dashboard Comercial / Financeiro)
├── requirements.txt          # Dependências do projeto para deploy
└── README.md                 # Documentação completa do projeto
```

---

## 🚀 Passo a Passo: Configuração do Supabase (Cloud Gratuito)

### 1. Criar o Projeto no Supabase
1. Acesse [supabase.com](https://supabase.com) e crie uma conta gratuita.
2. Clique em **"New Project"**, defina um nome (ex: `dw-b3-streamlit`) e guarde a sua **Database Password**.

### 2. Criar a Tabela `acoes_b3`
Você pode criar a tabela de duas maneiras simples:
* **Via SQL Editor:** Vá no menu **SQL Editor**, abra o arquivo [`schema_supabase.sql`](schema_supabase.sql), cole o conteúdo e clique em **Run**.
* **Via Table Editor (Importação direta de CSV):**
  1. Vá em **Table Editor** -> **New Table** (nome: `acoes_b3`).
  2. Clique em **Insert** -> **Import data from CSV** e selecione o arquivo [`dados_b3_reais.csv`](dados_b3_reais.csv).

### 3. (Opcional) Subir via Script Python
Se preferir automatizar a carga via Python:
```bash
python load_supabase.py
```

---

## 🔒 Configuração de Segredos (`secrets.toml`)

1. No diretório `.streamlit/`, copie o arquivo de exemplo:
   * No Windows PowerShell: `Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml`
2. No painel do Supabase, vá em **Project Settings -> Database -> Connection string** (selecione a aba **Parameters** ou **URI**).
3. Preencha o seu `.streamlit/secrets.toml`:

```toml
[connections.postgresql]
dialect = "postgresql"
host = "aws-0-us-east-2.pooler.supabase.com"
port = 6543
database = "postgres"
username = "postgres.adtvjcplizwuellgzuyr"
password = "postgres_local_pbi"
```

> **Nota de Resiliência:** Caso você não configure o `secrets.toml` ou fique sem internet, o aplicativo continuará funcionando normalmente através do **mecanismo de fallback** para o arquivo `dados_b3_reais.csv`!

---

## 💻 Executando o Projeto Localmente

1. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
2. Execute o Streamlit:
   ```bash
   streamlit run app.py
   ```
3. O painel abrirá automaticamente no seu navegador em `http://localhost:8501`.

---

## ☁️ Deploy no Streamlit Community Cloud

1. Suba este projeto para um repositório no seu **GitHub** (verifique se o `.gitignore` está ativo para não enviar senhas!).
2. Acesse [share.streamlit.io](https://share.streamlit.io) e faça login com seu GitHub.
3. Clique em **"New app"** e selecione:
   * **Repository:** seu repositório
   * **Branch:** `main`
   * **Main file path:** `app.py`
4. Antes de clicar em Deploy, clique em **Advanced settings... -> Secrets**.
5. Cole exatamente o conteúdo do seu `.streamlit/secrets.toml` no campo de texto e clique em **Save**.
6. Clique em **Deploy!** Em menos de 2 minutos seu dashboard estará online com link público acessível.
