"""
Teste para identificar o seletor correto do botão de paginação do TJDFT
"""

from playwright.sync_api import sync_playwright
import time

print("=" * 70)
print("🔍 TESTE: Identificar botão de paginação do TJDFT")
print("=" * 70)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Acessar página de resultados
    url = "https://jurisdf.tjdft.jus.br/resultado?sinonimos=true&espelho=true&inteiroTeor=true&textoPesquisa=fornecimento%20de%20medicação"
    print(f"\n📄 Acessando: {url}")
    page.goto(url, wait_until="networkidle")

    print("⏳ Aguardando 5 segundos...")
    time.sleep(5)

    print("\n🔍 Procurando elementos de paginação...")

    # Listar todos os botões
    botoes = page.query_selector_all("button")
    print(f"\n📊 Total de botões na página: {len(botoes)}")

    print("\n🔍 Botões com 'arrow', 'next', 'navigation' ou 'paginator':")
    for i, botao in enumerate(botoes):
        classes = botao.get_attribute("class") or ""
        aria_label = botao.get_attribute("aria-label") or ""
        disabled = botao.get_attribute("disabled")
        texto = botao.inner_text().strip()

        if any(
            keyword in classes.lower()
            or keyword in aria_label.lower()
            or keyword in texto.lower()
            for keyword in ["arrow", "next", "navigation", "pagina", "keyboard"]
        ):
            print(f"\n  [{i+1}] Classe: {classes[:80]}")
            print(f"      Aria-label: {aria_label}")
            print(f"      Texto: {texto[:50]}")
            print(f"      Disabled: {disabled}")

    # Tentar encontrar mat-paginator
    print("\n🔍 Procurando por mat-paginator...")
    paginator = page.query_selector(".mat-paginator")
    if paginator:
        print("✅ mat-paginator encontrado!")
        print(f"   HTML: {paginator.inner_html()[:200]}")
    else:
        print("❌ mat-paginator NÃO encontrado")

    # Tentar encontrar botões de navegação específicos
    seletores_teste = [
        'button[aria-label="Next page"]',
        'button[aria-label="Próxima página"]',
        ".mat-paginator-navigation-next",
        "button.mat-paginator-navigation-next",
        'button:has-text("keyboard_arrow_right")',
    ]

    print("\n🔍 Testando seletores específicos:")
    for seletor in seletores_teste:
        elemento = page.query_selector(seletor)
        if elemento:
            print(f"✅ ENCONTRADO: {seletor}")
            print(f"   Disabled: {elemento.get_attribute('disabled')}")
            print(f"   Aria-disabled: {elemento.get_attribute('aria-disabled')}")
        else:
            print(f"❌ NÃO encontrado: {seletor}")

    print("\n⏸️  Pausado para inspeção manual...")
    print("   Pressione ENTER para fechar o navegador...")
    input()

    browser.close()
    print("\n✅ Teste concluído!")
