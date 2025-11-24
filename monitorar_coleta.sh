#!/bin/bash
# Script para monitorar coleta em tempo real

echo "=========================================="
echo "📊 MONITORAMENTO DA COLETA - 750 PROCESSOS"
echo "=========================================="
echo ""

while true; do
    clear
    echo "=========================================="
    echo "📊 MONITORAMENTO DA COLETA - 750 PROCESSOS"
    echo "=========================================="
    echo ""
    
    # Verificar se processo está rodando
    if pgrep -f "python src/scraper_playwright_tjdft.py" > /dev/null; then
        echo "✅ Status: RODANDO"
    else
        echo "❌ Status: PARADO"
    fi
    
    echo ""
    echo "📈 Progresso no log:"
    echo "-------------------------------------------"
    
    # Contar processos coletados
    total=$(grep -c "✅ \[" coleta_750.log 2>/dev/null || echo "0")
    echo "   Processos coletados: $total / 750"
    
    # Calcular progresso
    if [ "$total" -gt 0 ]; then
        pct=$(echo "scale=1; ($total / 750) * 100" | bc)
        echo "   Progresso: ${pct}%"
    fi
    
    echo ""
    echo "🔍 Últimas 15 linhas do log:"
    echo "-------------------------------------------"
    tail -15 coleta_750.log 2>/dev/null || echo "Log não encontrado"
    
    echo ""
    echo "-------------------------------------------"
    echo "Atualizado em: $(date '+%H:%M:%S')"
    echo "Pressione Ctrl+C para sair"
    
    sleep 10
done
