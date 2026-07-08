# Análise Comparativa de Despesas por Função nas Capitais Brasileiras

## Problema e Contexto

Este projeto é uma solução para o **Desafio Técnico de Estágio em Análise de Dados** da [Sefaz Maceió](descricao_desafio.md).

O desafio consiste em analisar dados de **despesas das 26 capitais brasileiras** no período de **2020 a 2025**, publicados pelo **Siconfi** (Sistema de Contas Públicas do Tesouro Nacional). O objetivo principal é **comparar como as capitais gastam o dinheiro público por área (função)**, com foco na diferença entre o **empenhado** (reservado/comprometido) e o **pago** (efetivamente desembolsado).

Para contexto completo sobre os dados, requisitos e motivação do desafio, consulte o arquivo [descricao_desafio.md](descricao_desafio.md).

---

## Arquitetura da Solução

A solução segue o **padrão Medallion** de arquitetura de dados, dividindo o processamento em camadas claramente definidas:

```
Dados Compactos (ZIP)
       ↓
    [extract.py]
       ↓
Dados Extraídos - Bronze
(CSVs descompactados)
       ↓
    [transform.py]
       ↓
Dados Processados - Silver/Gold
(Parquet consolidado e validado)
       ↓
    [validate.py]
       ↓
DuckDB (Banco em memória, colunar)
       ↓
Análises via SQL + Notebooks
(Exploração, visualização, insights)
```


## Estrutura de Pastas

```
.
├── README.md                          # Este arquivo
├── pyproject.toml                     # Configuração do projeto (dependências, metadata)
├── database.duckdb                    # Arquivo do banco DuckDB (criado após pipeline)
├── dados_compactos/                   # Camada Raw: arquivos ZIP originais por ano
│   ├── 2020/
│   ├── 2021/
│   ├── ...
│   └── 2025/
├── dados_extraidos/                   # Camada Bronze: CSVs descompactados
│   ├── 2020/
│   │   └── finbra.csv
│   ├── 2021/
│   │   └── finbra.csv
│   └── ...
├── dados_processados/                 # Camada Silver/Gold: dados validados e otimizados
│   ├── finbra_consolidado.parquet     # Consolidação de todos os CSVs (após transform)
│   └── finbra_deflacionado.parquet    # Dados deflacionados (após deflação)
├── notebooks/                         # Análises exploratórias e visualizações
│   ├── analise_exploratoria.ipynb
│   ├── analise_descritiva.ipynb
│   └── ...
├── src/
│   ├── pipeline.py                    # Orquestrador principal do ETL
│   ├── query_exploratoria.py          # Queries SQL pré-definidas para exploração
│   ├── query_descritiva.py            # Queries SQL para análise descritiva
│   ├── config/                        # Configurações centralizadas
│   │   ├── ConexaoBanco.py            # Gerenciador de conexão DuckDB
│   │   ├── DataFrameConfig.py         # Schemas e validação Pandera
│   │   ├── Paths.py                   # Gerenciamento de caminhos
│   │   ├── logs.py                    # Configuração de logs
│   │   └── grafico.py                 # Funções auxiliares para visualização
│   ├── scripts/                       # Scripts de processamento (ETL)
│   │   ├── extract.py                 # Extração: descompacta ZIPs
│   │   ├── transform.py               # Transformação: limpeza e consolidação em Parquet
│   │   └── validate.py                # Validação: verifica integridade dos dados
│   ├── deflacao/                      # Módulo de deflação
│   │   ├── deflacao.py                # Lógica de deflação (pandas e DuckDB)
│   │   └── ipca_utils.py              # Utilitários para consulta API SIDRA (IPCA)
│   └── visualizacao/                  # Funções de geração de gráficos
│       ├── bar_ranking_pagamento_divida.py
│       ├── frequencia.py
│       ├── linha_comparativo_cultura_per_capita.py
│       ├── linha_comparativo_taxa_execucao.py
│       ├── linha_deflacao.py
│       └── linha_evolucao_subfuncoes_cultura.py
└── tests/                             # Testes unitários (cobertura: happy path, alternative paths, sad path)
    ├── test_extract.py                # Testes da extração
    ├── test_transform.py              # Testes da transformação
    ├── test_validate.py               # Testes da validação
    └── test_pipeline.py               # Testes de integração do pipeline
```

### Descrição dos Scripts Principais

- **pipeline.py**: Orquestrador do ETL. Executa extract → transform → validate em sequência, gerenciando logs e tratamento de erros.
- **extract.py**: Percorre `dados_compactos/`, localiza arquivos ZIP por ano e os extrai para `dados_extraidos/`.
- **transform.py**: Lê cada CSV com tratamento correto de encoding, separador decimal e skip de linhas de metadados. Consolida tudo em um único DataFrame, cria colunas derivadas (ano, tipo de conta) e salva em Parquet.
- **validate.py**: Valida o Parquet consolidado com schemas Pandera, verificando tipos, valores nulos, ranges e regras de negócio.
- **query_exploratoria.py** e **query_descritiva.py**: Queries SQL pré-definidas armazenadas como templates, para reutilização consistente nos notebooks.

---

## Decisões Técnicas

### 1. Padrão Medallion (Bronze → Silver → Gold)

O padrão Medallion organiza dados em camadas progressivas de qualidade e uso. Embora pequeno em escala, este padrão oferece:
- **Separação clara de responsabilidades**: cada camada tem um propósito definido
- **Auditoria**: é possível rastrear transformações
- **Reutilização**: dados bronze podem ser consumidos por múltiplos pipelines

### 2. Parquet como Formato de Armazenamento

Em vez de manter dados em CSV, utilizamos **Parquet** para a camada Silver/Gold:
- **Compressão**: reduz tamanho em disco (~80-90% menor que CSV)
- **Tipagem**: suporta tipos estruturados, garantindo consistência
- **Performance**: leitura colunar é muito mais rápida para consultas analíticas
- **Validação com Pandera**: schemas Parquet são validados contra regras de negócio

### 3. Validação com Pandera

Cada transformação é seguida de validação contra um schema Pandera que define:
- Tipos de dados obrigatórios
- Ranges de valores (ex.: população > 0)
- Valores nulos permitidos/proibidos
- Regras de negócio (ex.: Pago ≤ Empenhado)

Isso garante qualidade de dados antes de consumo em análises.

### 4. DuckDB para Consultas Analíticas

**Por que DuckDB, mesmo com poucos dados?**

Embora os dados caibam na memória de qualquer computador moderno, a escolha do DuckDB é estratégica:
- **Banco analítico colunar**: otimizado para agregações e filtros (não OLTP)
- **Em memória**: sem overhead de servidor externo
- **SQL padrão**: permite praticar e aprender SQL de forma prática
- **Objetivo pedagógico**: simular um ambiente de análise realista

DuckDB carrega o Parquet uma única vez e permite múltiplas consultas sem reprocessamento.

### 5. Notebooks para Exploração

Os Jupyter Notebooks consomem dados via DuckDB usando SQL pré-definido em `query_exploratoria.py` e `query_descritiva.py`, gerando:
- Análises exploratórias iniciais
- Gráficos dinâmicos (via Plotly, matplotlib, seaborn)
- Hipóteses e descobertas

Isso mantém separação clara entre ETL (scripts) e análise (notebooks).

---

## Como Executar

### Pré-requisitos

- Python 3.10+
- Git (para clonar o repositório)

### Passo 1: Clonar o Repositório

```bash
git clone <seu-repositorio>
cd Desafio-Analista-de-Dados-Sefaz-Macei-
```

### Passo 2: Criar e Ativar Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar (Windows)
.venv\Scripts\activate

# Ativar (Linux/Mac)
source .venv/bin/activate
```

### Passo 3: Instalar Dependências

```bash
# Instala o projeto em modo editable com todas as dependências
pip install -e .
```

O arquivo `pyproject.toml` especifica todas as dependências necessárias:
- pandas, polars (manipulação de dados)
- pandera (validação de schemas)
- duckdb (banco analítico)
- plotly, matplotlib, seaborn (visualização)
- requests (consulta API SIDRA)
- pytest (testes unitários)

### Passo 4: Executar o Pipeline ETL

```bash
python src/pipeline.py
```

Este comando:
1. Extrai todos os ZIPs de `dados_compactos/` → `dados_extraidos/`
2. Consolida CSVs em um único Parquet validado → `dados_processados/finbra_consolidado.parquet`
3. Cria banco DuckDB → `database.duckdb`
4. Aplica validações e loga resultados

Após execução bem-sucedida, você terá:
- `dados_processados/finbra_consolidado.parquet` (dados silver)
- `database.duckdb` (banco carregado com os dados)

### Passo 5: Executar Análises

Abra os notebooks em Jupyter:

```bash
jupyter notebook notebooks/
```

Recomenda-se começar por:
1. `analise_exploratoria.ipynb` - exploração inicial dos dados
2. `analise_descritiva.ipynb` - análises descritivas e descobertas

---

## Deflação de Dados

### Motivação

Comparar valores ao longo de múltiplos anos sem ajuste inflacionário leva a conclusões enganosas. Um gasto de R$ 1 milhão em 2020 tinha poder de compra diferente em 2025.

### Implementação

O módulo `src/deflacao/` implementa deflação usando:

- **API SIDRA**: consulta pública do IBGE para séries do IPCA (Índice de Preços ao Consumidor Amplo)
- **ipca_utils.py**: funções para baixar índices acumulados por período
- **deflacao.py**: implementações de deflação em **pandas** e **DuckDB**

#### Por que Pandas e DuckDB?

- **Pandas**: a resposta da API vem como JSON → DataFrame. Usamos pandas para processar esses dados brutos.
- **DuckDB**: uma vez processados, usamos SQL via DuckDB para deflacionar o Parquet consolidado de forma eficiente.

#### Por que um Novo Parquet em vez de Substituir?

Mantemos dois arquivos Parquet separados:
- `finbra_consolidado.parquet` (valores nominais originais)
- `finbra_deflacionado.parquet` (valores em moeda constante de referência, ex.: 2025)

**Razões:**

1. **Auditoria**: é possível rastrear dados originais vs. transformados
2. **Flexibilidade**: diferentes análises podem precisar de valores nominais ou reais
3. **Reprodutibilidade**: mudanças futuras na metodologia não perdem histórico
4. **Boas práticas**: não mutamos dados raw (imutabilidade de dados)

---

## Análises Disponíveis

Os notebooks executam análises explorando diferentes ângulos:

### [analise_exploratoria.ipynb](notebooks/analise_exploratoria.ipynb)

Exploração inicial dos dados:
- Dimensões do dataset (quantas capitais, anos, funções)
- Distribuição de despesas por função
- Completude de dados por ano
- Outliers e padrões iniciais

### [analise_descritiva.ipynb](notebooks/analise_descritiva.ipynb)

Análises descritivas focadas no desafio:
- **Taxa de Execução Financeira**: `(Despesas Pagas / Despesas Empenhadas) × 100`
  - Qual capital cumpre melhor suas empenhos?
  - Em quais funções há mais atraso (restos a pagar)?
- **Per Capita**: gasto por habitante por função
  - Comparação justa entre capitais de tamanhos diferentes
- **Evolução Temporal**: tendências 2020-2024
  - Crescimento/redução de gastos por função
  - Impacto de mudanças políticas ou crises
- **Análise por Subfunção**: detalhamento dentro de funções principais
  - Ex.: dentro de Saúde, quanto vai para Atenção Básica?

Gráficos gerados incluem rankings, evoluções temporais, comparativos per capita e heatmaps de execução.

---

## Testes

O projeto inclui testes unitários em `tests/`:

### Cobertura de Testes

- **Happy Path**: fluxo normal, dados válidos, saída esperada
- **Alternative Paths**: variações válidas (ex.: arquivo vazio, ano com dados parciais)
- **Sad Path**: erros esperados (ex.: arquivo corrompido, encoding inválido, schema violado)

### Executar Testes

```bash
# Todos os testes
pytest tests/

# Com cobertura
pytest tests/ --cov=src
```

### Arquivos de Teste

- `test_extract.py`: valida descompactação de ZIPs e localização de arquivos
- `test_transform.py`: valida leitura de CSVs com encoding/decimal corretos, consolidação e geração de colunas derivadas
- `test_validate.py`: valida schemas Pandera e regras de negócio
- `test_pipeline.py`: testes de integração do fluxo completo




## Licença

Projeto desenvolvido como solução para o Desafio Técnico de Estágio em Análise de Dados - Sefaz Maceió (2026).

