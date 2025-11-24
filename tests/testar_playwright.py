"""
Teste rápido do Playwright - Verifica se consegue acessar o site TJDFT
"""
from playwright.sync_api import sync_playwright
import time

def testar_acesso():
    print("🧪 Testando Playwright com TJDFT...\n")
    
    with sync_playwright() as p:
        # Iniciar navegador (headless=False para ver)
        print("1. Iniciando navegador...")
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Navegar para o site
        url = "https://jurisdf.tjdft.jus.br/resultado?sinonimos=true&espelho=true&inteiroTeor=true&textoPesquisa=fornecimento%20de%20medica%C3%A7%C3%A3o"
        print(f"2. Acessando: {url}")
        page.goto(url, wait_until='networkidle')
        
        # Aguardar carregamento
        print("3. Aguardando carregamento...")
        time.sleep(5)
        
        # Obter texto da página
        texto = page.inner_text('body')
        
        # Salvar screenshot
        page.screenshot(path='teste_playwright.png')
        print("4. Screenshot salvo: teste_playwright.png")
        
        # Verificar se encontrou resultados
        print(f"\n📊 Análise:")
        print(f"   Tamanho do texto: {len(texto)} caracteres")
        print(f"   Contém 'Processo:': {'✅ Sim' if 'Processo' in texto else '❌ Não'}")
        print(f"   Contém 'Relator': {'✅ Sim' if 'Relator' in texto else '❌ Não'}")
        print(f"   Contém 'medicamento': {'✅ Sim' if 'medicamento' in texto.lower() else '❌ Não'}")
        
        # Mostrar amostra
        print(f"\n📄 Primeiros 500 caracteres:")
        print("="*60)
        print(texto[:500])
        print("="*60)
        
        # Salvar texto completo
        with open('teste_playwright.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
        print("\n💾 Texto completo salvo em: teste_playwright.txt")
        
        input("\n⏸️  Pressione Enter para fechar o navegador...")
        
        browser.close()
        print("\n✅ Teste concluído!")

if __name__ == "__main__":
    testar_acesso()
