#!/bin/bash

# Script para configurar e testar o Gemini

echo "🔧 Configuração da API do Google Gemini"
echo ""
echo "1. Obtenha sua chave GRATUITA em:"
echo "   https://makersuite.google.com/app/apikey"
echo ""
echo "2. Cole sua chave abaixo (ou pressione Ctrl+C para cancelar):"
echo ""

read -p "GEMINI_API_KEY: " api_key

if [ -z "$api_key" ]; then
    echo "❌ Nenhuma chave fornecida. Saindo..."
    exit 1
fi

# Exportar para a sessão atual
export GEMINI_API_KEY="$api_key"

# Salvar em arquivo .env para uso futuro
echo "GEMINI_API_KEY=$api_key" > .env
echo ""
echo "✅ Chave salva em .env"
echo ""

# Testar
echo "🧪 Testando conexão..."
python3 << EOF
import os
os.environ['GEMINI_API_KEY'] = '$api_key'

from validador_gemini import ValidadorGemini

validador = ValidadorGemini()

if validador.habilitado:
    print("✅ API do Gemini configurada com sucesso!")
    print("")
    print("Testando validação...")
    
    resultado = validador.validar_processo(
        numero_processo="0711915-93.2024.8.07.0001",
        relator="LUCIMEIRE MARIA DA SILVA",
        medicamento="SOMATROPINA",
        decisao="CONHECER. NEGAR PROVIMENTO. UNÂNIME",
        texto_contexto="APELAÇÃO CÍVEL. PLANO DE SAÚDE."
    )
    
    print(f"Relator: LUCIMEIRE MARIA DA SILVA")
    print(f"Gênero identificado: {resultado['genero_relator']} (confiança: {resultado['confianca_genero']}%)")
    print(f"Medicamento válido: {'Sim' if resultado['medicamento_valido'] else 'Não'}")
    print("")
    print("✅ Teste concluído com sucesso!")
else:
    print("❌ Erro ao configurar API")
EOF

echo ""
echo "Para usar em futuros scripts, execute:"
echo "export GEMINI_API_KEY='$api_key'"
echo ""
echo "Ou adicione ao seu ~/.bashrc:"
echo "echo 'export GEMINI_API_KEY=\"$api_key\"' >> ~/.bashrc"
