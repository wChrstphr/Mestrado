"""
Teste para validar nova ordem de colunas
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.scraper_playwright_tjdft import ScraperPlaywright

print("=" * 70)
print("🧪 TESTE: Nova ordem de colunas (sem medicamento_sugerido_ia)")
print("=" * 70)

scraper = ScraperPlaywright(headless=False, usar_validador=True)

try:
    scraper.iniciar()
    scraper.buscar_termo("fornecimento de medicação", limite=3)

    df = scraper.salvar_resultados(
        arquivo_csv="teste_nova_ordem.csv", arquivo_json="teste_nova_ordem.json"
    )

    if df is not None:
        print("\n" + "=" * 70)
        print("📊 ORDEM DAS COLUNAS:")
        print("=" * 70)
        for i, col in enumerate(df.columns, 1):
            print(f"{i:2d}. {col}")

        print("\n" + "=" * 70)
        print("✅ Arquivos gerados:")
        print("   - data/raw/teste_nova_ordem.csv")
        print("   - data/raw/teste_nova_ordem.json")
        print("=" * 70)

finally:
    scraper.fechar()
