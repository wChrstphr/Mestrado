# 🏛️ Análise de Viés de Gênero em Sentenças Judiciais

**Pergunta de Pesquisa:** Há diferença de sentimento na sentença de juízes e juízas no Brasil?

## 📋 Sobre o Projeto

Este projeto investiga possíveis diferenças no sentimento das decisões judiciais com base no gênero do(a) julgador(a), utilizando técnicas de PLN (Processamento de Linguagem Natural) e análise de sentimento em decisões sobre fornecimento de medicamentos do TJDFT.

## 🎯 Objetivos

1. Coletar 500+ sentenças/acórdãos do TJDFT sobre fornecimento de medicamentos
2. Identificar nome e gênero do(a) relator(a)
3. Aplicar análise de sentimento nos textos
4. Comparar sentimentos entre decisões de diferentes gêneros
5. Analisar se há viés estatisticamente significativo

## 📁 Estrutura do Projeto

```
Mestrado/
├── projeto_sentimento_judicial.py      # Pipeline completo (original)
├── extrator_manual_tjdft.py            # Extrator para textos copiados
├── scraper_tjdft_medicamentos.py       # Scraper básico (para sites estáticos)
├── scraper_selenium_tjdft.py           # Scraper com Selenium
├── testar_api.py                       # Teste de conectividade API Datajud
├── testar_tjdft.py                     # Teste site TJDFT
├── processos_ids_500.csv               # 500 IDs coletados da API Datajud
├── INSTRUCOES_COLETA.md                # Instruções detalhadas de coleta
├── requirements.txt                    # Dependências Python
└── README.md                           # Este arquivo
```

## 🚀 Como Usar

### 1. Instalação

```bash
# Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt
```

### 2. Coleta de Dados

#### Opção A: API Datajud (500 IDs coletados)
```bash
python projeto_sentimento_judicial.py --ids-apenas
```
✅ **Já executado!** Arquivo: `processos_ids_500.csv`

#### Opção B: Site TJDFT (Recomendado para o projeto)
Veja instruções detalhadas em `INSTRUCOES_COLETA.md`

**Método rápido:**
1. Acesse: https://jurisdf.tjdft.jus.br/resultado
2. Busque: "fornecimento de medicamento"
3. Use o script JavaScript no console (ver INSTRUCOES_COLETA.md)
4. Processe: `python extrator_manual_tjdft.py acordaos_tjdft.txt`

### 3. Análise

```bash
# Pipeline completo (após ter os textos)
python projeto_sentimento_judicial.py
```

## 📊 Dados Coletados

### API Datajud (Backup)
- **Total:** 500 processos
- **Tribunal:** TJDFT
- **Distribuição:**
  - G2 (2ª instância): 339
  - TR (Turma Recursal): 124
  - G1 (1ª instância): 37
- **Classes principais:**
  - Agravo de Instrumento: 159
  - Recurso Inominado Cível: 98
  - Apelação Cível: 97

### Site TJDFT (Em progresso)
- **Foco:** Fornecimento de medicamentos
- **Campos extraídos:**
  - Número do processo
  - Nome do(a) Relator(a)
  - Medicamento mencionado
  - Decisão final

## 🛠️ Tecnologias

- **Python 3.12+**
- **Pandas** - Manipulação de dados
- **Requests** - Requisições HTTP
- **BeautifulSoup4** - Parsing HTML
- **Selenium** (opcional) - Scraping de sites dinâmicos
- **Transformers** (futuro) - Análise de sentimento
- **spaCy** (futuro) - NER para extração de nomes

## 📝 Metodologia

1. **Coleta de Dados**
   - Web scraping respeitando robots.txt
   - Rate limiting (2-3s entre requisições)
   - Registro de metadata (data/hora de coleta)

2. **Identificação do Julgador**
   - Extração via regex e NER
   - Inferência de gênero por prenome
   - Marcação de casos ambíguos

3. **Análise de Sentimento**
   - Modelo BERT multilíngue para português
   - Foco na ementa ou dispositivo
   - Escala: positivo/neutro/negativo

4. **Análise Estatística**
   - Teste de hipóteses (t-test, chi-quadrado)
   - Controle de variáveis (assunto, ano, instância)
   - Visualizações comparativas

## ⚖️ Ética e Conformidade

- ✅ Dados públicos (jurisprudência)
- ✅ Anonimização quando necessário
- ✅ Transparência sobre limitações
- ✅ Documentação de erros e incertezas
- ✅ Respeito a termos de uso dos sites

## 📈 Próximos Passos

- [ ] Completar coleta de 500 textos completos do TJDFT
- [ ] Implementar análise de sentimento com BERT
- [ ] Melhorar extração de medicamentos com NER
- [ ] Expandir base de prenomes para inferência de gênero
- [ ] Validar manualmente amostra (precision/recall)
- [ ] Análise estatística comparativa
- [ ] Relatório técnico (10-15 páginas)
- [ ] Apresentação final (5-8 min)

## 🤝 Equipe

- Dupla/trio conforme definição da disciplina
- Perfis: técnico (implementação) + negócios (escopo/comunicação)

## 📚 Referências

- [API Pública Datajud - CNJ](https://datajud-wiki.cnj.jus.br/api-publica/)
- [TJDFT - Jurisprudência](https://jurisdf.tjdft.jus.br/)
- [Tabelas Processuais Unificadas (TPU)](https://www.cnj.jus.br/sgt/consulta_publica_classes.php)

## 📄 Licença

Projeto acadêmico - Mestrado em Políticas Públicas

---

**Data de última atualização:** 23/11/2025
