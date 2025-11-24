"""
Debug: Verificar o que acontece ao clicar em Detalhes
"""
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    
    url = "https://jurisdf.tjdft.jus.br/resultado?sinonimos=true&espelho=true&inteiroTeor=true&textoPesquisa=fornecimento%20de%20medica%C3%A7%C3%A3o"
    
    print("📍 Navegando...")
    page.goto(url)
    time.sleep(5)
    
    print("🔍 Procurando botão Detalhes...")
    page.wait_for_selector('button:has-text("Detalhes")', timeout=10000)
    
    botoes = page.query_selector_all('button:has-text("Detalhes")')
    print(f"✅ Encontrados {len(botoes)} botões")
    
    if len(botoes) > 0:
        print("\n🖱️  Clicando no primeiro botão...")
        botoes[0].click()
        time.sleep(3)
        
        print("\n📸 Salvando screenshot...")
        page.screenshot(path="debug_modal_aberto.png", full_page=True)
        
        print("\n📄 Tentando extrair texto do modal...")
        
        # Tentar diferentes seletores
        seletores = [
            ('juris-detalhes-acordao', 'Custom element'),
            ('mat-dialog-content', 'Material dialog'),
            ('[role="dialog"]', 'Dialog role'),
            ('.cdk-overlay-pane', 'CDK overlay'),
            ('.mat-dialog-container', 'Mat dialog container')
        ]
        
        for seletor, desc in seletores:
            try:
                elemento = page.query_selector(seletor)
                if elemento:
                    texto = elemento.inner_text()
                    print(f"\n✅ {desc} ({seletor}): {len(texto)} chars")
                    print(f"Primeiros 300 chars:")
                    print("-" * 60)
                    print(texto[:300])
                    print("-" * 60)
                else:
                    print(f"❌ {desc} ({seletor}): não encontrado")
            except Exception as e:
                print(f"❌ {desc} ({seletor}): erro - {e}")
        
        # Salvar HTML completo
        print("\n💾 Salvando HTML...")
        html = page.content()
        with open("debug_modal_html.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ HTML salvo (debug_modal_html.html) - {len(html)} chars")
        
        input("\n⏸️  Pressione ENTER para fechar...")
    
    browser.close()
    print("\n✅ Concluído!")
