"""
Script para ver o progresso da coleta do checkpoint
"""

import json
import os
from datetime import datetime

checkpoint_file = "data/raw/checkpoint.json"

print("=" * 70)
print("📊 STATUS DO CHECKPOINT")
print("=" * 70)

if not os.path.exists(checkpoint_file):
    print("\n❌ Nenhum checkpoint encontrado!")
    print(f"   Arquivo esperado: {checkpoint_file}")
    print("\n💡 Execute o scraper para iniciar a coleta:")
    print("   python src/scraper_playwright_tjdft.py")
else:
    with open(checkpoint_file, "r", encoding="utf-8") as f:
        checkpoint = json.load(f)

    total = checkpoint.get("total_processos", 0)
    proximo_id = checkpoint.get("proximo_id", 1)
    ultima_atualizacao = checkpoint.get("ultima_atualizacao", "N/A")

    print(f"\n✅ Checkpoint encontrado!")
    print(f"\n📈 Progresso:")
    print(f"   Processos coletados: {total}")
    print(f"   Meta: 750 processos")
    print(f"   Progresso: {(total/750)*100:.1f}%")
    print(f"   Próximo ID: {proximo_id}")

    if ultima_atualizacao != "N/A":
        try:
            dt = datetime.fromisoformat(ultima_atualizacao)
            print(f"\n🕒 Última atualização: {dt.strftime('%d/%m/%Y %H:%M:%S')}")
        except:
            print(f"\n🕒 Última atualização: {ultima_atualizacao}")

    if total > 0:
        resultados = checkpoint.get("resultados", [])

        # Estatísticas de gênero
        generos = {}
        medicamentos = {}
        decisoes_favoraveis = 0
        decisoes_desfavoraveis = 0

        for r in resultados:
            # Gênero
            genero = r.get("genero_relator", "Indeterminado")
            generos[genero] = generos.get(genero, 0) + 1

            # Medicamento
            med = r.get("medicamento", "N/A")
            if med and med != "N/A":
                medicamentos[med] = medicamentos.get(med, 0) + 1

            # Decisão
            if r.get("decisao_favoravel") == True:
                decisoes_favoraveis += 1
            elif r.get("decisao_favoravel") == False:
                decisoes_desfavoraveis += 1

        print(f"\n👥 Distribuição por gênero:")
        for genero, count in sorted(generos.items(), key=lambda x: x[1], reverse=True):
            pct = (count / total) * 100
            print(f"   {genero}: {count} ({pct:.1f}%)")

        if decisoes_favoraveis + decisoes_desfavoraveis > 0:
            print(f"\n⚖️  Decisões:")
            total_decisoes = decisoes_favoraveis + decisoes_desfavoraveis
            print(
                f"   Favoráveis: {decisoes_favoraveis} ({(decisoes_favoraveis/total_decisoes)*100:.1f}%)"
            )
            print(
                f"   Desfavoráveis: {decisoes_desfavoraveis} ({(decisoes_desfavoraveis/total_decisoes)*100:.1f}%)"
            )

        if medicamentos:
            print(f"\n💊 Top 5 medicamentos:")
            for med, count in sorted(
                medicamentos.items(), key=lambda x: x[1], reverse=True
            )[:5]:
                print(f"   {med}: {count}")

    print("\n" + "=" * 70)

    if total < 750:
        print(f"\n💡 Para continuar a coleta:")
        print(f"   python continuar_coleta.py")
    else:
        print(f"\n✅ Meta atingida! Para salvar os resultados finais:")
        print(f"   python src/scraper_playwright_tjdft.py")

    print("=" * 70)
