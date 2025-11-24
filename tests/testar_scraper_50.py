"""
Teste do scraper completo - Coleta processos da primeira página com detalhes
"""

import sys
from pathlib import Path

# Adiciona o diretório pai ao PATH para permitir imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scraper_playwright_tjdft import ScraperPlaywright


def teste_coleta_pequena():
    """Testa coleta de processos com modal de detalhes"""
    print("🧪 TESTE: Coletando processos com detalhes completos...\n")

    scraper = ScraperPlaywright(
        headless=False, usar_validador=True
    )  # COM validador Gemini!

    try:
        # Iniciar
        scraper.iniciar()

        # Coletar apenas 3 da primeira página (para teste muito rápido)
        scraper.buscar_termo("fornecimento de medicação", limite=3)

        # Salvar
        df = scraper.salvar_resultados(
            arquivo_csv="teste_detalhes_processos.csv",
            arquivo_json="teste_detalhes_processos.json",
        )

        # Mostrar amostra
        if df is not None and not df.empty:
            print("\n" + "=" * 60)
            print("📋 AMOSTRA (primeiros 3):")
            print("=" * 60)
            for idx, row in df.head(3).iterrows():
                print(f"\n{idx+1}. Processo: {row['numero_processo']}")
                print(f"   Relator: {row['relator']}")
                print(f"   Medicamento: {row['medicamento']}")

                decisao = row["decisao"]
                if decisao and len(str(decisao)) > 150:
                    decisao = str(decisao)[:150] + "..."
                print(f"   Decisão: {decisao}")

        print("\n✅ Teste concluído! Verifique a qualidade dos dados.")

    finally:
        scraper.fechar()


if __name__ == "__main__":
    teste_coleta_pequena()
