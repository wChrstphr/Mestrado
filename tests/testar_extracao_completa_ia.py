"""
Teste do validador com TEXTO COMPLETO - IA extrai tudo
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.validador_gemini import ValidadorGemini

print("=" * 70)
print("🧪 TESTE: IA EXTRAI TUDO DO TEXTO COMPLETO")
print("=" * 70)

validador = ValidadorGemini()

if not validador.habilitado:
    print("❌ Validador não habilitado!")
    exit(1)

print("\n✅ Validador inicializado!")
print()

# Texto completo real de um processo
texto_completo = """
Acórdão 2064522
Processo: 0711915-93.2024.8.07.0001

Relator(a) LUCIMEIRE MARIA DA SILVA
5ª TURMA CÍVEL
13/11/2025
Publicado no PJe: 19/11/2025

Ementa:
APELAÇÃO CÍVEL. PLANO DE SAÚDE. ENTIDADE DE AUTOGESTÃO. INAPLICABILIDADE DO CDC. 
FORNECIMENTO DE MEDICAMENTO. SOMATROPINA. ROL DA ANS. USO DOMICILIAR. NEGATIVA INDEVIDA. 
REEMBOLSO DE DESPESAS. SUCUMBÊNCIA MÍNIMA.

1. O Instituto de Assistência à Saúde dos Servidores do Distrito Federal – INAS/DF é autarquia 
em regime especial, regida por normas próprias, não se aplicando as disposições do Código de 
Defesa do Consumidor (Súmula 608/STJ).

2. O medicamento Somatropina prescrito à autora foi inserido no "Protocolo Clínico e Diretrizes 
Terapêuticas Deficiência de Hormônio do Crescimento - Hipopituitarismo" aprovado pela Conitec 
em março de 2018.

3. A negativa de cobertura fundada exclusivamente no fato de o medicamento ser de uso domiciliar 
é abusiva quando se tratar de tratamento essencial à enfermidade coberta pelo plano e incluído 
no rol da ANS.

4. Comprovada a negativa indevida e a necessidade do tratamento, é devido o reembolso integral 
das quantias despendidas para aquisição do fármaco, observada a coparticipação contratual.

5. Reconhecida a sucumbência mínima da autora, impõe-se ao réu o pagamento integral das despesas 
processuais e honorários advocatícios.

6. Apelos conhecidos. Recurso do réu desprovido. Recurso da autora provido.

Decisão:
CONHECER. NEGAR PROVIMENTO AO APELO DO RÉU. DAR PROVIMENTO AO APELO DA AUTORA. UNÂNIME
"""

print("=" * 70)
print("TESTE: Passar TEXTO COMPLETO para IA extrair tudo")
print("=" * 70)
print("\nℹ️  Não passamos relator, medicamento ou decisão extraídos!")
print("   A IA vai extrair TUDO do texto completo.\n")

# Chamar validador SEM passar dados extraídos (só texto completo)
resultado = validador.validar_processo(
    numero_processo="0711915-93.2024.8.07.0001",
    relator="",  # VAZIO! IA vai extrair
    medicamento="",  # VAZIO! IA vai extrair
    decisao="",  # VAZIO! IA vai extrair
    texto_completo=texto_completo,
)

print("=" * 70)
print("📊 RESULTADO DA EXTRAÇÃO PELA IA")
print("=" * 70)

print(f"\n👤 RELATOR:")
print(f"   Nome extraído: {resultado.get('genero_relator', 'N/A')}")
print(f"   Gênero: {resultado['genero_relator']}")
print(f"   Confiança: {resultado['confianca_genero']}%")

print(f"\n💊 MEDICAMENTO:")
print(f"   Nome extraído: {resultado.get('medicamento_extraido', 'N/A')}")
print(f"   É válido? {resultado.get('medicamento_valido')}")

print(f"\n⚖️  DECISÃO:")
print(f"   Texto extraído: {resultado.get('decisao_extraida', 'N/A')}")
print(f"   Favorável ao paciente? {resultado.get('decisao_favoravel')}")

print(f"\n📝 OBSERVAÇÕES:")
print(f"   {resultado.get('observacoes', 'N/A')}")

print(f"\n{'='*70}")

# Validar se a IA extraiu corretamente
acertos = []
erros = []

if "LUCIMEIRE" in (resultado.get("medicamento_extraido", "") or "").upper():
    erros.append("❌ ERRO: IA confundiu nome da juíza com medicamento!")
else:
    acertos.append("✅ IA não confundiu nome da juíza")

if "SOMATROPINA" in (resultado.get("medicamento_extraido", "") or "").upper():
    acertos.append("✅ IA extraiu medicamento correto: SOMATROPINA")
else:
    erros.append("❌ ERRO: IA não encontrou SOMATROPINA")

if resultado.get("genero_relator") == "F":
    acertos.append("✅ IA identificou gênero correto: Feminino")
else:
    erros.append(f"❌ ERRO: Gênero incorreto: {resultado.get('genero_relator')}")

if resultado.get("decisao_favoravel") == True:
    acertos.append("✅ IA identificou decisão favorável corretamente")
else:
    erros.append("❌ ERRO: Decisão deveria ser favorável (deu provimento à autora)")

if "CONHECER" in (resultado.get("decisao_extraida", "") or ""):
    acertos.append("✅ IA extraiu texto da decisão")
else:
    erros.append("❌ ERRO: IA não extraiu texto da decisão")

print("\n📊 AVALIAÇÃO FINAL:")
print("=" * 70)
for acerto in acertos:
    print(acerto)
for erro in erros:
    print(erro)

print(f"\n{'='*70}")
print(f"✅ Acertos: {len(acertos)}/{len(acertos)+len(erros)}")
print(f"❌ Erros: {len(erros)}/{len(acertos)+len(erros)}")
print(f"{'='*70}")

if len(erros) == 0:
    print("\n🎉 PERFEITO! A IA extraiu e validou TUDO corretamente!")
    print("   Agora o scraper pode enviar o texto completo e a IA faz o resto!")
else:
    print(f"\n⚠️  Algumas extrações falharam. Revisar prompt da IA.")
