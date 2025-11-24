"""
Teste simples do Validador Gemini
"""

import sys
from pathlib import Path
import os

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.validador_gemini import ValidadorGemini

print("=" * 70)
print("🧪 TESTE VALIDADOR GEMINI")
print("=" * 70)

# Inicializar
validador = ValidadorGemini()

if not validador.habilitado:
    print("❌ Validador não habilitado!")
    exit(1)

print("\n✅ Validador inicializado com sucesso!")
print(f"📦 Modelo: gemini-2.5-flash")
print()

# Teste 1: Validação individual
print("=" * 70)
print("TESTE 1: Validação de processo individual")
print("=" * 70)

resultado = validador.validar_processo(
    numero_processo="0711915-93.2024.8.07.0001",
    relator="LUCIMEIRE MARIA DA SILVA",
    medicamento="SOMATROPINA",
    decisao="CONHECER. NEGAR PROVIMENTO AO APELO DO RÉU. DAR PROVIMENTO AO APELO DA AUTORA. UNÂNIME",
    texto_contexto="APELAÇÃO CÍVEL. PLANO DE SAÚDE. FORNECIMENTO DE MEDICAMENTO. SOMATROPINA...",
)

print(f"\n📊 Resultado:")
print(f"   👤 Relator: LUCIMEIRE MARIA DA SILVA")
print(
    f"   🤖 Gênero: {resultado['genero_relator']} (Confiança: {resultado['confianca_genero']}%)"
)
print(f"   💊 Medicamento: SOMATROPINA")
print(f"   ✓ Válido: {resultado['medicamento_valido']}")
if resultado["medicamento_corrigido"]:
    print(f"   📝 Sugestão: {resultado['medicamento_corrigido']}")
print(f"   📋 Obs: {resultado['observacoes']}")

# Teste 2: Mais casos
print("\n" + "=" * 70)
print("TESTE 2: Outros casos")
print("=" * 70)

casos = [
    ("ANA CANTARINO", "ZOMETA"),
    ("JANSEN FIALHO DE ALMEIDA", "ZOMETA"),
    ("MAURICIO SILVA MIRANDA", "SPRAVATO"),
    ("CARLOS PIRES SOARES NETO", "SPRAVATO"),
]

for relator, med in casos:
    print(f"\n⏳ Validando {relator}...")
    resultado = validador.validar_processo(
        numero_processo="teste",
        relator=relator,
        medicamento=med,
        decisao="CONHECER. UNÂNIME",
        texto_contexto=f"Processo sobre {med}",
    )
    print(
        f"   🤖 Gênero: {resultado['genero_relator']} (Confiança: {resultado['confianca_genero']}%)"
    )
    print(f"   💊 Medicamento válido: {resultado['medicamento_valido']}")

print("\n" + "=" * 70)
print("✅ TODOS OS TESTES CONCLUÍDOS!")
print("=" * 70)
