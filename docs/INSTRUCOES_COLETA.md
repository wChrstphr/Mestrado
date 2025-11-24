# Instruções para Coleta de Dados - TJDFT

## 🎯 Objetivo
Coletar 500 casos sobre fornecimento de medicamentos do TJDFT

## 📝 Método Recomendado

### Opção 1: Coleta Manual Assistida (Mais Simples)

O site do TJDFT usa JavaScript dinâmico, então a melhor abordagem é:

1. **Acessar o site:**
   ```
   https://jurisdf.tjdft.jus.br/resultado?sinonimos=true&espelho=true&inteiroTeor=true&textoPesquisa=fornecimento%20de%20medicamento
   ```

2. **Navegar pelas páginas e copiar os textos**
   - Abra o console do navegador (F12)
   - Execute o seguinte JavaScript para extrair automaticamente:
   
   ```javascript
   // Cole isso no Console do navegador
   let resultados = [];
   let cards = document.querySelectorAll('.card-resultado, article, [class*="resultado"]');
   
   cards.forEach((card, i) => {
       let texto = card.innerText;
       if (texto.includes('Processo') && (texto.includes('fornecimento') || texto.includes('medicamento'))) {
           resultados.push(texto);
       }
   });
   
   // Copiar para área de transferência
   copy(resultados.join('\n\n===SEPARADOR===\n\n'));
   console.log(`Copiados ${resultados.length} resultados para a área de transferência!`);
   ```

3. **Colar em um arquivo de texto**
   - Criar arquivo `acordaos_tjdft.txt`
   - Colar o conteúdo copiado

4. **Processar com nosso script:**
   ```bash
   python extrator_manual_tjdft.py acordaos_tjdft.txt
   ```

### Opção 2: Usar Selenium (Automático)

1. **Instalar dependências:**
   ```bash
   pip install selenium webdriver-manager
   ```

2. **Executar o scraper:**
   ```bash
   python scraper_selenium_tjdft.py
   ```

### Opção 3: Inspecionar API do Site

1. **Abrir DevTools (F12) > Network**
2. **Filtrar por XHR/Fetch**
3. **Fazer uma busca no site**
4. **Procurar por requisições a APIs** (ex: `/api/busca`, `/search`, etc.)
5. **Replicar a requisição diretamente**

## 🔍 Informações a Extrair

Para cada processo:
- ✅ Número do processo (formato CNJ)
- ✅ Nome do(a) Relator(a)
- ✅ Medicamento mencionado
- ✅ Decisão final

## 📊 Meta

- **Total desejado:** 500 processos
- **Termos de busca:**
  - "fornecimento de medicamento"
  - "fornecimento de medicação"
- **Tribunal:** TJDFT
- **Tipo:** Acórdãos/Decisões

## ⚠️ Importante

- Respeitar robots.txt
- Implementar delays entre requisições (2-3 segundos)
- Documentar o método de coleta no relatório
- Manter log das etapas

## 📂 Arquivos Disponíveis

1. `extrator_manual_tjdft.py` - Processa textos copiados manualmente
2. `scraper_selenium_tjdft.py` - Scraper automatizado (requer Selenium)
3. `scraper_tjdft_medicamentos.py` - Scraper para sites estáticos (não funciona para TJDFT)

## 🚀 Próximos Passos Após Coleta

1. **Limpeza de dados**
2. **Identificação de gênero** dos relatores
3. **Extração de nomes de medicamentos** com NLP
4. **Análise de sentimento** das decisões
5. **Análise estatística** comparando gêneros
