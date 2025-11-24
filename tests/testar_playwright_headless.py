"""
Teste Playwright em modo headless (sem interface gráfica)
"""
from playwright.sync_api import sync_playwright
import time

def testar_acesso_headless():
    print("🧪 Testando Playwright com TJDFT (modo headless)...\n")
    
    with sync_playwright() as p:
        # Iniciar navegador em modo headless
        print("1. Iniciando navegador (headless)...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Navegar para o site
        url = "https://jurisdf.tjdft.jus.br/resultado?sinonimos=true&espelho=true&inteiroTeor=true&textoPesquisa=fornecimento%20de%20medica%C3%A7%C3%A3o"
        print(f"2. Acessando: {url}")
        page.goto(url, wait_until='networkidle', timeout=30000)
        
        # Aguardar carregamento
        print("3. Aguardando carregamento...")
        time.sleep(5)
        
        # Obter texto da página
        texto = page.inner_text('body')
        
        # Salvar screenshot
        page.screenshot(path='teste_playwright_headless.png', full_page=True)
        print("4. Screenshot salvo: teste_playwright_headless.png")
        
        # Verificar se encontrou resultados
        print(f"\n📊 Análise:")
        print(f"   Tamanho do texto: {len(texto)} caracteres")
        print(f"   Contém 'Processo:': {'✅ Sim' if 'Processo' in texto else '❌ Não'}")
        print(f"   Contém 'Relator': {'✅ Sim' if 'Relator' in texto else '❌ Não'}")
        print(f"   Contém 'medicamento': {'✅ Sim' if 'medicamento' in texto.lower() else '❌ Não'}")
        print(f"   Contém 'Acórdão': {'✅ Sim' if 'Acórdão' in texto else '❌ Não'}")
        
        # Contar números de processo
        import re
        processos = re.findall(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', texto)
        print(f"   Números de processo encontrados: {len(processos)}")
        
        # Mostrar amostra
        print(f"\n📄 Primeiros 800 caracteres:")
        print("="*60)
        print(texto[:800])
        print("="*60)
        
        # Salvar texto completo
        with open('teste_playwright_headless.txt', 'w', encoding='utf-8') as f:
            f.write(texto)
        print("\n💾 Texto completo salvo em: teste_playwright_headless.txt")
        
        # Mostrar alguns processos encontrados
        if processos:
            print(f"\n🔍 Primeiros 5 processos encontrados:")
            for i, proc in enumerate(processos[:5], 1):
                print(f"   {i}. {proc}")
        
        browser.close()
        print("\n✅ Teste concluído!")
        
        return len(processos) > 0

if __name__ == "__main__":
    sucesso = testar_acesso_headless()
    if sucesso:
        print("\n🎉 Site acessível! Pronto para scraping automatizado.")
    else:
        print("\n⚠️  Nenhum processo encontrado. Verifique a URL ou aguarde mais tempo.")
