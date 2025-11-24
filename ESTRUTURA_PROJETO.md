# 📁 Estrutura do Projeto - Análise de Sentimento Judicial

## 📂 Organização de Pastas

```
Mestrado/
├── 📁 src/                          # Código-fonte principal
│   ├── scraper_playwright_tjdft.py   # Scraper principal (Playwright)
│   ├── validador_gemini.py           # Validador com Gemini API
│   └── projeto_sentimento_judicial.py # Pipeline completo
│
├── 📁 tests/                        # Scripts de teste
│   ├── testar_scraper_50.py          # Teste rápido (3-50 processos)
│   ├── testar_playwright.py          # Teste básico Playwright
│   ├── testar_playwright_headless.py # Teste headless
│   ├── testar_modal_*.py             # Testes de modal
│   ├── testar_api.py                 # Teste API CNJ
│   ├── testar_tjdft.py               # Teste site TJDFT
│   └── extrator_manual_tjdft.py      # Extrator manual (fallback)
│
├── 📁 scripts/                      # Scripts auxiliares
│   ├── configurar_gemini.sh          # Configuração Gemini API
│   ├── extrair_navegador.js          # Extração via console (manual)
│   ├── extrair_simples.js            # Extração simplificada
│   ├── scraper_selenium_alternativo.py # Alternativa com Selenium
│   └── scraper_antigo.py             # Versão antiga do scraper
│
├── 📁 docs/                         # Documentação
│   ├── README.md                     # Visão geral do projeto
│   ├── GUIA_RAPIDO.md                # Início rápido
│   ├── GUIA_GEMINI.md                # Configuração Gemini
│   ├── INSTRUCOES_COLETA.md          # Instruções de coleta
│   ├── RESUMO_MELHORIAS.md           # Changelog
│   └── RESUMO_PROGRESSO.txt          # Histórico de progresso
│
├── 📁 data/                         # Dados do projeto
│   ├── raw/                          # Dados brutos coletados
│   │   ├── processos_ids_500.csv     # IDs da API CNJ
│   │   ├── teste_50_processos.*      # Testes de coleta
│   │   └── teste_detalhes_processos.* # Testes com detalhes
│   └── processed/                    # Dados processados (futuro)
│       └── (análises e resultados finais)
│
├── 📁 logs/                         # Logs de execução
│   ├── coleta_*.log                  # Logs de coleta
│   └── scraping_playwright_*.log     # Logs do Playwright
│
├── 📁 temp/                         # Arquivos temporários
│   ├── debug_*.html                  # HTML de debug
│   ├── debug_*.png                   # Screenshots de debug
│   └── debug_*.txt                   # Textos de debug
│
├── 📄 .env                          # Variáveis de ambiente (API keys)
├── 📄 requirements.txt               # Dependências Python
└── 📁 venv/                         # Ambiente virtual Python
```

## 🚀 Como Usar

### 1. Configuração Inicial
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências (se necessário)
pip install -r requirements.txt

# Configurar Gemini API (opcional)
./scripts/configurar_gemini.sh
```

### 2. Executar Testes
```bash
# Teste rápido (3 processos)
python tests/testar_scraper_50.py

# Teste da API
python tests/testar_api.py
```

### 3. Coleta Completa
```bash
# Scraper principal (500 processos)
python src/scraper_playwright_tjdft.py

# Pipeline completo (coleta + análise)
python src/projeto_sentimento_judicial.py
```

## 📊 Fluxo de Trabalho

1. **Desenvolvimento/Teste** → `tests/`
2. **Coleta de Dados** → `src/scraper_playwright_tjdft.py` → `data/raw/`
3. **Validação** → `src/validador_gemini.py`
4. **Análise** → `src/projeto_sentimento_judicial.py` → `data/processed/`
5. **Logs** → `logs/`

## 📝 Arquivos Importantes

- **`src/scraper_playwright_tjdft.py`**: Scraper principal ⭐
- **`src/validador_gemini.py`**: Validação com IA
- **`tests/testar_scraper_50.py`**: Teste rápido antes de coletar tudo
- **`docs/GUIA_RAPIDO.md`**: Instruções de uso
- **`scripts/configurar_gemini.sh`**: Setup da API

## 🔧 Manutenção

### Limpar arquivos temporários
```bash
rm -rf temp/*
rm -rf logs/*.log
```

### Backup de dados
```bash
tar -czf backup_$(date +%Y%m%d).tar.gz data/raw/
```

## 📚 Documentação

Consulte a pasta `docs/` para mais informações:
- Guias de uso
- Instruções de coleta
- Melhorias implementadas
- Troubleshooting

---

**Última atualização**: 23/11/2025
**Versão**: 2.0 (Organizada)
