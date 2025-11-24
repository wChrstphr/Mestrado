"""
Script para continuar coleta do checkpoint
Se a coleta foi interrompida, este script continua de onde parou
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.scraper_playwright_tjdft import ScraperPlaywright

print("=" * 70)
print("🔄 CONTINUAR COLETA DO CHECKPOINT")
print("=" * 70)

# Inicializar scraper (vai carregar checkpoint automaticamente)
scraper = ScraperPlaywright(headless=False, usar_validador=True)

print(f"\n📊 Status do checkpoint:")
print(f"   Processos já coletados: {len(scraper.resultados)}")
print(f"   Próximo ID: {scraper.proximo_id}")
print()

if len(scraper.resultados) >= 750:
    print("✅ Meta de 750 processos já atingida!")
    print("   Execute o script principal para salvar os resultados finais.")
else:
    processos_faltam = 750 - len(scraper.resultados)
    print(f"🎯 Continuando coleta... Faltam {processos_faltam} processos")
    print()

    try:
        scraper.iniciar()

        # Continuar coletando os termos
        termos = ["fornecimento de medicação", "fornecimento de medicamento"]

        for termo in termos:
            if len(scraper.resultados) >= 750:
                break

            processos_restantes = 750 - len(scraper.resultados)
            scraper.buscar_termo(termo, limite=processos_restantes)

        # Salvar resultados
        df = scraper.salvar_resultados(
            arquivo_csv="tjdft_medicamentos_playwright.csv",
            arquivo_json="tjdft_medicamentos_playwright.json",
        )

        print("\n" + "=" * 70)
        print("✅ COLETA CONTINUADA CONCLUÍDA!")
        print("=" * 70)

    finally:
        scraper.fechar()
