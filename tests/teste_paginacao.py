"""
Teste de paginação - coletar 25 processos (mais de 1 página)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

from src.scraper_playwright_tjdft import ScraperPlaywright

print("=" * 70)
print("🧪 TESTE: Paginação (25 processos = ~2 páginas)")
print("=" * 70)

scraper = ScraperPlaywright(headless=False, usar_validador=True)

try:
    scraper.iniciar()
    scraper.buscar_termo("fornecimento de medicação", limite=25)

    df = scraper.salvar_resultados(
        arquivo_csv="teste_paginacao.csv", arquivo_json="teste_paginacao.json"
    )

    if df is not None:
        print("\n" + "=" * 70)
        print(f"✅ Teste concluído!")
        print(f"   Total de processos: {len(df)}")
        print(f"   Esperado: 25")
        print(f"   Sucesso: {'SIM ✅' if len(df) == 25 else 'NÃO ❌'}")
        print("=" * 70)

finally:
    scraper.fechar()
