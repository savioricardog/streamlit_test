-- ==============================================================================
-- SCRIPT DE CRIAÇÃO DA TABELA NO SUPABASE (SQL Editor)
-- ==============================================================================

-- 1. Criação da tabela de cotações da B3
CREATE TABLE IF NOT EXISTS acoes_b3 (
    id BIGSERIAL PRIMARY KEY,
    data DATE NOT NULL,
    preco_fechamento NUMERIC(10, 4) NOT NULL,
    volume BIGINT NOT NULL,
    ticker VARCHAR(10) NOT NULL
);

-- 2. Índices para acelerar consultas e filtros por data e ticker
CREATE INDEX IF NOT EXISTS idx_acoes_b3_ticker ON acoes_b3 (ticker);
CREATE INDEX IF NOT EXISTS idx_acoes_b3_data ON acoes_b3 (data);

-- Observação para importação:
-- Você pode importar o arquivo 'dados_b3_reais.csv' diretamente no Supabase em:
-- Table Editor -> acoes_b3 -> Insert -> Import data from CSV
