# Lei de Zipf: textos humanos vs. textos gerados por IA

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Descrição

Pipeline de engenharia de dados para comparar a distribuição de Zipf entre textos
humanos (Project Gutenberg) e textos gerados por inteligência artificial (Groq API).
O projeto estima o coeficiente **α** da Lei de Zipf por regressão linear no espaço
log-log e compara estatisticamente os dois corpora.

## Objetivo científico

A Lei de Zipf estabelece que, em um corpus de linguagem natural, a frequência de
uma palavra é inversamente proporcional ao seu rank: **f ∝ r⁻ᵅ**, com α ≈ 1 para
textos humanos. Este experimento investiga se textos gerados por LLMs seguem a
mesma distribuição ou apresentam desvios significativos.

### Hipótese nula (H₀)

A distribuição dos coeficientes α de textos gerados por IA é igual à de textos
humanos.

### Métricas

- **α** — coeficiente de Zipf (inclinação no gráfico log-log)
- **R²** — qualidade do ajuste linear
- **KS test** — teste de Kolmogorov-Smirnov entre as duas distribuições

## Arquitetura

O projeto segue os princípios de **Clean Architecture** e **Separation of Concerns**,
organizado em camadas com responsabilidades bem definidas:

```
┌──────────────────────────────────────────────────────────┐
│                       main.py                            │
│              (ponto de entrada — só inicia)              │
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────┐
│                  pipelines/pipeline.py                    │
│         (orquestrador — coordena o fluxo completo)        │
└──┬────────┬────────┬────────┬────────┬────────┬─────────┘
   │        │        │        │        │        │
   ▼        ▼        ▼        ▼        ▼        ▼
┌──────┐ ┌────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌────────┐
│ data │ │ models │ │analysis│ │ vis  │ │ utils│ │ config │
│loader│ │ groq_  │ │zipf + │ │plots │ │logger│ │ .py    │
│pre-  │ │generat │ │statist│ │      │ │file_ │ │        │
│proc. │ │or      │ │ics    │ │      │ │manag.│ │        │
└──────┘ └────────┘ └──────┘ └──────┘ └──────┘ └────────┘
```

### Fluxo do pipeline

Cada livro percorre as seguintes etapas, com **cache** e **checkpoint**:

```
Book ID
   │
   ▼
┌──────────────────┐
│ Download Gutenberg│ ───> data/raw/{id}.txt
└──────────────────┘
   │
   ▼
┌──────────────────┐
│  Preprocess      │ ───> data/processed/{id}.txt
└──────────────────┘
   │
   ▼
┌──────────────────┐     ┌──────────────────────────┐
│ Cache check      │────>│ Se existe em              │
│ data/generated/  │  │  │ data/generated/{id}.txt   │
└──────────────────┘  │  │ → carrega do disco        │
   │                  └──│ Se não → chama API Groq   │
   ▼                     └──────────────────────────┘
┌──────────────────┐
│  Calcular Zipf   │
│  (humano + IA)   │
└──────────────────┘
   │
   ▼
┌──────────────────┐
│  Salvar resultado│ ───> outputs/zipf_results.csv
└──────────────────┘
   │
   ▼
┌──────────────────┐
│  Gerar gráficos  │ ───> outputs/figures/
└──────────────────┘
```

### Checkpoint e reinicialização

O pipeline lê o arquivo `outputs/zipf_results.csv` ao iniciar para identificar
quais livros já foram processados. Se a execução for interrompida (ex.: no
livro 83 de 100), ao reiniciar ela continua automaticamente do livro 84.

### Cache de geração IA

Textos artificiais são salvos em `data/generated/{book_id}.txt`. Se o arquivo
já existir, a API não é chamada — o texto é lido diretamente do disco.

## Estrutura do projeto

```
.
├── data/
│   ├── raw/            # Textos brutos do Gutenberg
│   ├── processed/      # Textos limpos e normalizados
│   ├── generated/      # Textos gerados por IA (cache)
│   └── external/       # Dados externos de referência
│
├── outputs/
│   ├── figures/        # Gráficos gerados (PNG, 300dpi)
│   ├── tables/         # Tabelas de resultados (CSV)
│   └── reports/        # Relatórios de prompt (markdown)
│
├── logs/               # Logs do pipeline
│
├── notebooks/          # Jupyter notebooks para exploração
│
├── src/
│   ├── data/
│   │   ├── loader.py           # Download de livros do Gutenberg
│   │   └── preprocessing.py    # Limpeza e normalização de texto
│   │
│   ├── pipelines/
│   │   └── pipeline.py         # Orquestração do experimento
│   │
│   ├── models/
│   │   └── groq_generator.py   # Interface com a API Groq
│   │
│   ├── analysis/
│   │   ├── zipf.py             # Cálculos da Lei de Zipf
│   │   └── statistics.py       # Indicadores estatísticos
│   │
│   ├── visualization/
│   │   └── plots.py            # Geração de gráficos
│   │
│   ├── utils/
│   │   ├── logger.py           # Configuração de logging
│   │   ├── file_manager.py     # Operações de arquivo
│   │   └── helpers.py          # Funções auxiliares
│   │
│   └── config.py               # Configurações centralizadas
│
├── tests/
│   ├── test_preprocessing.py
│   ├── test_zipf.py
│   ├── test_statistics.py
│   └── test_file_manager.py
│
├── main.py                     # Ponto de entrada
├── requirements.txt            # Dependências
├── pyproject.toml              # Configuração do projeto
└── .env.example                # Template de variáveis de ambiente
```

## Tecnologias utilizadas

| Categoria        | Ferramenta                           |
|------------------|--------------------------------------|
| Linguagem        | Python 3.10+                         |
| Geração de texto | Groq API (LLaMA 3.1 8B)              |
| Computação científica | NumPy                           |
| Análise de dados | pandas, SciPy                        |
| Visualização     | Matplotlib                           |
| HTTP             | requests                             |
| Configuração     | python-dotenv                        |
| Testes           | pytest                               |
| Qualidade        | ruff                                 |

## Instalação

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/zipf-human-vs-ai.git
cd zipf-human-vs-ai

# Criar ambiente virtual
python -m venv .venv

# Ativar (Windows)
.venv\Scripts\activate

# Ativar (Linux/macOS)
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Instalar o projeto em modo editável (opcional)
pip install -e .
```

## Configuração

Copie o arquivo de template e edite com suas chaves:

```bash
cp .env.example .env
```

Configure no `.env`:

```env
GROQ_API_KEY=sua_chave_aqui
GROQ_MODEL=llama-3.1-8b-instant
TARGET_WORDS=5000
MAX_BOOKS=100
```

## Execução

```bash
python main.py
```

Para uma execução rápida de validação:

```env
MAX_BOOKS=2
TARGET_WORDS=500
ACCEPTABLE_DIFFERENCE=100
```

### Resultados gerados

Após a execução, os seguintes artefatos são produzidos:

| Arquivo                         | Descrição                          |
|---------------------------------|------------------------------------|
| `outputs/zipf_results.csv`      | Resultados por livro (α, R²)       |
| `outputs/tables/descriptive_statistics.csv` | Média, mediana, desvio, min, max |
| `outputs/tables/ks_test.csv`    | Teste Kolmogorov-Smirnov           |
| `outputs/figures/alpha_histogram.png`   | Histograma dos coeficientes α      |
| `outputs/figures/alpha_boxplot.png`     | Boxplot humano vs. IA              |
| `outputs/figures/alpha_density.png`     | Densidade dos coeficientes         |
| `outputs/figures/r2_histogram.png`      | Distribuição do R²                 |
| `outputs/figures/zipf_loglog_fit.png`   | Ajuste log-log de exemplo          |
| `logs/pipeline.log`             | Log detalhado da execução          |

## Testes

```bash
pip install -r requirements-dev.txt
pytest
```

## Reproduzibilidade

Para reproduzir o experimento:

1. Configure uma chave da Groq em `.env`
2. Execute `python main.py`
3. Os resultados serão salvos em `outputs/` com timestamp nos logs

O pipeline é **idempotente**: se interrompido, retoma do último checkpoint.
Textos artificiais já gerados são reutilizados via cache em `data/generated/`.

## Licença

MIT License. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## Autores

- Daniel Alves Thielmann
- Felipe Gotelip Delgado
