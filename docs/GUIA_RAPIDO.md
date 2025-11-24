# 🚀 GUIA RÁPIDO - Coleta de Dados TJDFT

## ⚡ Método Mais Simples (RECOMENDADO)

### Passo 1: Abrir o site
```
https://jurisdf.tjdft.jus.br/resultado?sinonimos=true&espelho=true&inteiroTeor=true&textoPesquisa=fornecimento%20de%20medicamento
```

### Passo 2: Abrir Console do Navegador
- Pressione **F12**
- Clique na aba **Console**

### Passo 3: Copiar TUDO da página
Cole este comando no console e pressione Enter:

```javascript
copy(document.body.innerText);
```

✅ **Pronto!** O texto foi copiado para sua área de transferência.

### Passo 4: Colar em arquivo
- Abra um editor de texto (VS Code, Notepad, etc.)
- Crie arquivo: `acordaos_tjdft.txt`
- Cole o conteúdo (Ctrl+V)

### Passo 5: Repetir para mais páginas
1. No site, clique em "Próxima página" ou navegue pelos resultados
2. Repita o Passo 3 (copy...)
3. Cole **NO FINAL** do mesmo arquivo `acordaos_tjdft.txt`
4. Adicione uma linha separadora: `===NOVA_PAGINA===`
5. Repita até ter conteúdo suficiente (~10-15 páginas)

### Passo 6: Processar os dados
No terminal:
```bash
cd /home/chrstphr/Mestrado
source venv/bin/activate
python extrator_manual_tjdft.py acordaos_tjdft.txt
```

✅ Isso gerará um arquivo CSV estruturado!

---

## 🔧 Método Alternativo (Script Inteligente)

Se quiser usar o script que filtra automaticamente:

### Opção A: Script Completo
Cole no console: (todo o conteúdo de `extrair_navegador.js`)

### Opção B: Script Simples  
Cole no console: (todo o conteúdo de `extrair_simples.js`)

---

## 📊 Quantos dados coletar?

- **Meta:** 500 processos
- **Páginas estimadas:** 10-20 páginas de resultados
- **Tempo estimado:** 30-60 minutos

---

## ❓ Problemas Comuns

### "Nenhum resultado encontrado"
- ✅ Aguarde a página carregar completamente (5-10 segundos)
- ✅ Use o método simples: `copy(document.body.innerText);`

### "Erro ao copiar"
- ✅ Alguns navegadores bloqueiam clipboard
- ✅ O script mostrará o texto no console - copie manualmente

### "Script não funciona"
- ✅ Use sempre o método mais simples primeiro
- ✅ Verifique se está na aba Console (não Elements ou Network)

---

## 🎯 Checklist

- [ ] Abri o site do TJDFT
- [ ] Fiz a busca por "fornecimento de medicamento"
- [ ] Abri o Console (F12)
- [ ] Executei: `copy(document.body.innerText);`
- [ ] Colei em arquivo `acordaos_tjdft.txt`
- [ ] Repeti para 10+ páginas
- [ ] Executei: `python extrator_manual_tjdft.py acordaos_tjdft.txt`
- [ ] Verifiquei o arquivo CSV gerado

---

## 📞 Próximo Passo Após Coleta

Quando tiver o CSV com os dados:

```bash
# Ver estatísticas
python -c "import pandas as pd; df = pd.read_csv('tjdft_medicamentos.csv'); print(df.info()); print(df.head())"
```

Depois seguir com:
1. Análise de sentimento
2. Inferência de gênero
3. Análise estatística
