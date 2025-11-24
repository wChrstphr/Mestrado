# 📊 COLETA DE 750 PROCESSOS - STATUS

## ✅ Configuração Atual

**Meta**: 750 processos judiciais sobre fornecimento de medicamentos
**Termos de busca**: 
- "fornecimento de medicação" (375 processos)
- "fornecimento de medicamento" (375 processos)

**Filtros aplicados**:
- ❌ Ignora processos SEM medicamento
- ❌ Ignora medicamentos genéricos: "MEDICAÇÃO", "MEDICAMENTO", "PRESCRITO", "REGISTRADO", "PRODUTO", etc.
- ✅ Salva apenas processos com nome específico de medicamento

**Validação Gemini**: DESABILITADA
- Motivo: Quota de 250 requisições/dia excedida
- Solução: Coletar dados hoje, validar amanhã

## 🚀 Processo em Execução

**Comando**: 
```bash
python src/scraper_playwright_tjdft.py
```

**Log**: `coleta_750.log`

**Velocidade estimada**: 
- ~4 segundos por processo (sem Gemini)
- Tempo total estimado: ~50 minutos

## 💾 Arquivos Gerados

**Durante a coleta**:
- `data/raw/checkpoint.json` - Salvo a cada 5 processos
- `coleta_750.log` - Log em tempo real

**Ao finalizar**:
- `data/raw/tjdft_medicamentos_playwright.csv` - Dados em CSV
- `data/raw/tjdft_medicamentos_playwright.json` - Dados em JSON

## 📋 Estrutura dos Dados

**Colunas** (ordem):
1. `id` - ID sequencial (1, 2, 3...)
2. `numero_processo` - Número CNJ
3. `relator` - Nome do relator
4. `medicamento` - Nome do medicamento
5. `decisao` - Texto da decisão
6. `termo_busca` - Termo usado na busca
7. `data_coleta` - Data/hora da coleta
8. `texto_completo` - Texto completo do acórdão (3000 chars)

**Campos que serão preenchidos AMANHÃ com Gemini**:
- `genero_relator` - Gênero identificado pela IA
- `confianca_genero` - Confiança da identificação (%)
- `medicamento_validado` - Se medicamento é válido
- `decisao_favoravel` - Se decisão foi favorável ao paciente
- `decisao_extraida_ia` - Decisão extraída pela IA
- `observacoes_validacao` - Observações da IA

## 🔧 Comandos Úteis

**Monitorar progresso em tempo real**:
```bash
./monitorar_coleta.sh
```

**Ver progresso do checkpoint**:
```bash
python ver_progresso.py
```

**Verificar últimas linhas do log**:
```bash
tail -f coleta_750.log
```

**Contar processos coletados**:
```bash
grep -c "✅ \[" coleta_750.log
```

**Se precisar interromper**:
```bash
pkill -f "python src/scraper_playwright_tjdft.py"
```

**Continuar de onde parou** (usa checkpoint):
```bash
python continuar_coleta.py
```

## 📅 Próximos Passos (Amanhã)

1. **Validar com Gemini**:
   - Executar script de validação nos 750 processos coletados
   - Identificar gênero dos relatores
   - Analisar favorabilidade das decisões
   - Validar medicamentos

2. **Análise de Sentimento**:
   - Comparar decisões de juízes masculinos vs femininos
   - Análise estatística da favorabilidade por gênero
   - Gerar gráficos e relatórios

## ⚠️ Observações Importantes

- **Checkpoint automático**: Salva progresso a cada 5 processos
- **Duplicatas removidas**: Sistema detecta e ignora processos repetidos
- **Paginação funcional**: Usa botão "navigate_next" do TJDFT
- **ID único**: Cada processo recebe ID sequencial para controle
