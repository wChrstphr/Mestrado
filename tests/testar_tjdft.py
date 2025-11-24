"""
Teste rápido para verificar estrutura do site TJDFT
"""
import requests
from bs4 import BeautifulSoup
import json

URL = "https://jurisdf.tjdft.jus.br/resultado?sinonimos=true&espelho=true&inteiroTeor=true&textoPesquisa=fornecimento%20de%20medica%C3%A7%C3%A3o"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
}

print("🔍 Testando acesso ao TJDFT...")
print(f"URL: {URL}\n")

try:
    response = requests.get(URL, headers=HEADERS, timeout=30)
    print(f"✅ Status Code: {response.status_code}")
    print(f"   Tamanho da resposta: {len(response.text)} bytes\n")
    
    # Salvar HTML para análise
    with open('tjdft_sample.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("💾 HTML salvo em: tjdft_sample.html")
    
    # Parse básico
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Tentar encontrar estrutura de resultados
    print("\n🔍 Procurando estruturas HTML comuns...")
    
    # Verificar tags comuns
    tags_interesse = ['article', 'div.card', 'div.resultado', 'div.item', 'section']
    for tag in tags_interesse:
        elementos = soup.select(tag) if '.' in tag else soup.find_all(tag)
        if elementos:
            print(f"   ✅ Encontrado {len(elementos)} elemento(s): <{tag}>")
    
    # Procurar por "Processo:" no texto
    processos = soup.find_all(string=lambda text: text and 'Processo:' in text)
    print(f"   📄 Encontradas {len(processos)} menções a 'Processo:'")
    
    # Procurar por "Relator"
    relatores = soup.find_all(string=lambda text: text and 'Relator' in text)
    print(f"   👤 Encontradas {len(relatores)} menções a 'Relator'")
    
    # Procurar por "Decisão"
    decisoes = soup.find_all(string=lambda text: text and 'Decisão:' in text)
    print(f"   ⚖️  Encontradas {len(decisoes)} menções a 'Decisão:'")
    
    # Mostrar primeiros 2000 caracteres do HTML
    print(f"\n📄 Preview do HTML (primeiros 2000 chars):")
    print("="*60)
    print(response.text[:2000])
    print("="*60)
    
except Exception as e:
    print(f"❌ Erro: {e}")
