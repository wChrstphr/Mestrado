# Pipeline de Coleta de Dados para Machine Learning

Sistema para coleta e processamento de dados processuais do TJCE.

## 📁 Estrutura do Projeto

```
Mestrado/
├── coletar_dados_ml.py          # MAIN
├── scripts/
│   ├── __init__.py              # Inicialização do pacote
│   ├── scraper_tjce.py          # Módulo 1: Web Scraping
│   ├── inferir_sexo.py          # Módulo 2: Inferência de Sexo
│   ├── gerar_features.py        # Módulo 3: Geração de Features
│   └── analisar_features.py     # Análise exploratória
├── data/                        # Diretório de dados
│   ├── numeros_processos.csv    # Input: números de processos
│   ├── decisoes_resumo.csv      # Input: decisões judiciais
│   ├── dados_completos.json     # Input: dados completos do TJCE
│   ├── nomes.csv.gz            # Input: base de nomes brasileiros
│   ├── dados_processos_tjce.csv # Output: dados coletados
│   ├── dados_processos_com_sexo.csv # Output: dados + sexo
│   └── dataset_ml_completo.csv  # Output: dataset final (29 features)
└── requirements.txt             # Dependências do projeto
```

## 🚀 Uso Rápido

### Executar Pipeline Completo

```bash
python coletar_dados_ml.py
```

Isso executará todas as 3 etapas:
1. ✅ Web Scraping do TJCE
2. ✅ Inferência de Sexo
3. ✅ Geração de Features

### Executar Etapas Individualmente

```bash
# Apenas scraping
python coletar_dados_ml.py --etapa scraping

# Apenas inferência de sexo
python coletar_dados_ml.py --etapa inferir_sexo

# Apenas geração de features
python coletar_dados_ml.py --etapa features
```

### Executar Módulos Diretamente

```bash
# Módulo 1: Scraping
python scripts/scraper_tjce.py

# Módulo 2: Inferência de Sexo
python scripts/inferir_sexo.py

# Módulo 3: Geração de Features
python scripts/gerar_features.py
```

## 📊 Pipeline Detalhado

### Etapa 1: Web Scraping (scraper_tjce.py)

**Entrada:**
- `data/numeros_processos.csv` - Lista de números de processos
- `data/decisoes_resumo.csv` - Decisões judiciais

**Saída:**
- `data/dados_processos_tjce.csv` - Dados coletados (juiz, requerente, sentença)
- `data/cache_processos.json` - Cache de progresso

**Funcionalidades:**
- Navegação automatizada no site do TJCE com Playwright
- Extração de nome do juiz e requerente
- Sistema de cache para recuperação de falhas
- Salvamento automático a cada 50 processos

### Etapa 2: Inferência de Sexo (inferir_sexo.py)

**Entrada:**
- `data/dados_processos_tjce.csv`
- `data/nomes.csv.gz` - Base de nomes brasileiros

**Saída:**
- `data/dados_processos_com_sexo.csv`

**Funcionalidades:**
- Extração do primeiro nome de juízes e requerentes
- Busca em base de 130k+ nomes brasileiros
- Classificação: M (Masculino), F (Feminino), Indefinido

### Etapa 3: Geração de Features (gerar_features.py)

**Entrada:**
- `data/dados_completos.json` - Dados brutos do TJCE
- `data/dados_processos_com_sexo.csv`

**Saída:**
- `data/dataset_ml_completo.csv` - **29 features**

**Features Geradas:**

#### 1. Identificação (1)
- `numero_processo`

#### 2. Temporais (5)
- `dias_desde_ajuizamento`
- `ano_ajuizamento`, `mes_ajuizamento`
- `trimestre_ajuizamento`, `dia_semana_ajuizamento`

#### 3. Categóricas (6)
- `grau`, `classe_categoria`, `tipo_vara`
- `municipio_fortaleza`, `sistema`, `formato`

#### 4. Assuntos (7)
- `qtd_assuntos`, `tem_medicamento`, `tem_tutela_urgencia`
- `tem_obrigacao_fazer`, `tem_dano_moral`, `area_saude`
- `assunto_principal`

#### 5. Movimentos (4)
- `qtd_movimentos`, `velocidade_movimentos`
- `movimentos_recentes`, `tipo_distribuicao`

#### 6. Derivadas (2)
- `complexidade_score` (qtd_assuntos × qtd_movimentos)
- `tem_recurso`

#### 7. Sexo e Sentença (4)
- `sexo_juiz`, `sexo_requerente`
- `sentenca_favoravel`, `status`

## ⚙️ Instalação

### 1. Criar ambiente virtual

```bash
python -m venv venv
```

### 2. Ativar ambiente virtual

**Windows:**
```bash
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Instalar browsers do Playwright

```bash
playwright install chromium
```

## 📦 Dependências

- `playwright` - Automação web
- `pandas` - Manipulação de dados
- `numpy` - Operações numéricas
- `python-dateutil` - Manipulação de datas

### Orquestrador (coletar_dados_ml.py)

O orquestrador coordena a execução dos módulos:

- ✅ Verifica dependências e arquivos de entrada
- ✅ Executa etapas na ordem correta
- ✅ Valida saídas de cada etapa
- ✅ Fornece feedback detalhado ao usuário
- ✅ Permite execução parcial do pipeline

## 📝 Licença

Este projeto é parte de dissertação de mestrado de Giovanni Brigido Bezerra Cardoso.

## 👨‍💻 Autores

Giovanni Brigido Bezerra Cardoso - Mestrado em I.A e Ciência de Dados

Wanjo Christopher Paraizo Escobar - Graduando em Engenharia de Software
