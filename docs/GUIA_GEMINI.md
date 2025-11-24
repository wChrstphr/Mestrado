# 🤖 Guia Rápido: Validação com Gemini API

## O que foi implementado?

Agora o scraper pode usar **Google Gemini API (GRATUITA)** para:

1. **Identificar o gênero do relator/a** automaticamente
   - Ex: "LUCIMEIRE MARIA DA SILVA" → Feminino (F)
   - Ex: "JANSEN FIALHO DE ALMEIDA" → Masculino (M)

2. **Validar o nome do medicamento**
   - Verifica se é realmente um medicamento
   - Sugere correções se encontrar o nome correto no texto
   - Ex: Se extraiu "MEDICAÇÃO" mas o texto tem "SOMATROPINA", sugere a correção

3. **Melhorias na extração:**
   - ✅ Decisão completa (ex: "CONHECER. NEGAR PROVIMENTO. UNÂNIME")
   - ✅ Removida ementa (simplificação)
   - ✅ Foco em: relator, medicamento, decisão

## Como configurar?

### Passo 1: Obter chave API (GRÁTIS)

1. Acesse: https://makersuite.google.com/app/apikey
2. Faça login com sua conta Google
3. Clique em "Create API Key"
4. Copie a chave gerada

### Passo 2: Configurar no projeto

**Opção A - Script automático:**
```bash
./configurar_gemini.sh
```

**Opção B - Manual:**
```bash
export GEMINI_API_KEY="sua_chave_aqui"
```

**Opção C - Arquivo .env:**
```bash
echo "GEMINI_API_KEY=sua_chave_aqui" > .env
```

### Passo 3: Testar

```bash
python validador_gemini.py
```

## Como usar no scraper?

```python
from scraper_playwright_tjdft import ScraperPlaywright

# COM validação (recomendado)
scraper = ScraperPlaywright(headless=True, usar_validador=True)

# SEM validação
scraper = ScraperPlaywright(headless=True, usar_validador=False)
```

## Dados extraídos

Cada processo terá agora:

```json
{
  "numero_processo": "0711915-93.2024.8.07.0001",
  "relator": "LUCIMEIRE MARIA DA SILVA",
  "medicamento": "SOMATROPINA",
  "decisao": "CONHECER. NEGAR PROVIMENTO. UNÂNIME",
  
  // Novos campos com validação:
  "genero_relator": "F",
  "confianca_genero": 100,
  "medicamento_validado": true,
  "medicamento_sugerido": null,
  "observacoes_validacao": "Nome claramente feminino"
}
```

## Limites da API Gratuita

- ✅ **60 requisições por minuto**
- ✅ **1.500 requisições por dia**
- ✅ **Modelo: gemini-1.5-flash** (rápido e eficiente)

Para 500 processos = 500 requisições → **OK para uso diário**

## Próximos passos

1. Configure a API key
2. Teste com 3 processos: `python testar_scraper_50.py`
3. Se tudo OK, execute coleta completa: `python scraper_playwright_tjdft.py`

## Troubleshooting

**Erro: "GEMINI_API_KEY não configurada"**
→ Execute `export GEMINI_API_KEY="sua_chave"`

**Erro: "API quota exceeded"**
→ Aguarde 1 minuto ou use `usar_validador=False`

**Validação retorna "Indeterminado"**
→ Normal para nomes ambíguos ou desconhecidos

## Alternativa sem API

Se não quiser usar Gemini:
```python
scraper = ScraperPlaywright(headless=True, usar_validador=False)
```

O scraper funcionará normalmente, apenas sem a validação automática de gênero e medicamento.
