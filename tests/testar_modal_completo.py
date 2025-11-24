"""
Debug: Aguardar modal carregar completamente
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
        
        # Aguardar MAIS tempo para o modal carregar
        print("⏳ Aguardando 5 segundos para modal carregar completamente...")
        time.sleep(5)
        
        # Pegar TODO o conteúdo do body
        texto_completo = page.inner_text('body')
        
        print(f"\n📄 Texto total: {len(texto_completo)} chars")
        print("\n" + "="*80)
        print("CONTEÚDO COMPLETO:")
        print("="*80)
        print(texto_completo)
        print("="*80)
        
        # Salvar em arquivo para análise
        with open("debug_texto_completo.txt", "w", encoding="utf-8") as f:
            f.write(texto_completo)
        print("\n💾 Texto salvo em: debug_texto_completo.txt")
        
        input("\n⏸️  Pressione ENTER para fechar...")
    
    browser.close()
    print("\n✅ Concluído!")
