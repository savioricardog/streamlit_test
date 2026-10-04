# 🎓 Guia do Professor: Trilha Passo a Passo das Aulas

Este diretório contém os códigos de referência organizados exatamente no ponto de evolução ao término de cada aula da **Semana 11**:

---

## 📅 Aula 1 (Terça-feira): `aula_01_conexao_e_seguranca.py`
* **Foco:** Conexão nativa ao banco de dados relacional e gestão segura de credenciais.
* **O que rodar com os alunos:**
  ```bash
  streamlit run aulas/aula_01_conexao_e_seguranca.py
  ```
* **Destaques da aula:**
  1. Criação do `.gitignore` para omitir o `.streamlit/secrets.toml`.
  2. Conexão nativa com `st.connection("postgresql", type="sql")`.
  3. Resiliência: desligar o banco ou trocar a senha para mostrar o fallback em CSV funcionando.
  4. Prática guiada do **Slide 15**: consulta dinâmica com SQL parametrizado (`:ticker` e `params={"ticker": ...}`).

---

## 📅 Aula 2 (Quinta-feira): `aula_02_cache_filtros_estado.py`
* **Foco:** Otimização de performance com caching e interatividade reativa avançada.
* **O que rodar com os alunos:**
  ```bash
  streamlit run aulas/aula_02_cache_filtros_estado.py
  ```
* **Destaques da aula:**
  1. Problema do ciclo de reexecução (*Rerun Model*) do Streamlit e o gargalo no banco.
  2. Implementação do `@st.cache_data(ttl=600, show_spinner=...)`.
  3. Diferença entre `@st.cache_data` (dados) e `@st.cache_resource` (conexões).
  4. Barra lateral reativa com filtros cruzados (`st.multiselect` e `st.date_input`).
  5. Gerenciamento de estado com `st.session_state` e botão de reset com callback (`on_click`).

---

## 📅 Aula 3 (Sexta-feira): `aula_03_deploy_e_dashboard.py` (e `app.py` na raiz)
* **Foco:** Visualizações interativas ricas, indicadores de negócio e deploy em nuvem.
* **O que rodar com os alunos:**
  ```bash
  streamlit run aulas/aula_03_deploy_e_dashboard.py
  # Ou a versão completa profissional na raiz:
  streamlit run app.py
  ```
* **Destaques da aula:**
  1. Cartões de KPI executivos com `st.columns(4)` e `st.metric`.
  2. Gráficos dinâmicos em Plotly: histórico de preços, comparativo normalizado em Base 100 e volume diário.
  3. Geração do `requirements.txt` com `psycopg[binary]`.
  4. Publicação no GitHub e deploy no **Streamlit Community Cloud** com configuração de Secrets no painel web.
