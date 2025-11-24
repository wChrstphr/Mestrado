"""
Scraper para TJDFT usando Selenium (necessário para sites dinâmicos)
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'scraping_selenium_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ==================== FUNÇÕES DE EXTRAÇÃO ====================

def extrair_nome_medicamento(texto: str) -> Optional[str]:
    """Extrai nome de medicamento do texto."""
    if not texto:
        return None
    
    # Palavras em maiúsculas (típico de medicamentos)
    padroes = [
        r'\b([A-ZÁÉÍÓÚÂÃÔÊ]{3,}(?:\s+[A-ZÁÉÍÓÚÂÃÔÊ]{3,})?)\b',
        r'medicamento[:\s]+([A-ZÁÉÍÓÚÂÃÔÊa-záéíóúâãôêç]+)',
    ]
    
    exclusoes = {'APELAÇÃO', 'RECURSO', 'DECISÃO', 'SENTENÇA', 'TRIBUNAL', 'PLANO', 
                 'SAÚDE', 'FORNECIMENTO', 'CÍVEL', 'CRIMINAL', 'TURMA', 'ACÓRDÃO',
                 'PROCESSO', 'EMENTA', 'CONHECIDO', 'PROVIDO', 'IMPROVIDO', 'PARCIAL',
                 'COMARCA', 'INSTÂNCIA', 'RELATORA', 'RELATOR', 'JULGAMENTO'}
    
    for padrao in padroes:
        matches = re.findall(padrao, texto)
        for med in matches:
            med = med.strip()
            if med.upper() not in exclusoes and len(med) > 3:
                return med
    
    return None


# ==================== SCRAPER SELENIUM ====================

class ScraperTJDFTSelenium:
    """
    Scraper usando Selenium para sites dinâmicos
    """
    
    def __init__(self, headless: bool = True):
        """
        Inicializa o driver Selenium
        
        Args:
            headless: Se True, executa sem interface gráfica
        """
        logger.info("🚀 Inicializando Selenium...")
        
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        self.resultados = []
    
    def buscar_processos(self, termo: str, limite: int = 500) -> List[Dict]:
        """
        Busca processos no site do TJDFT
        """
        logger.info(f"🔍 Buscando por: '{termo}'")
        
        url = f"https://jurisdf.tjdft.jus.br/resultado?sinonimos=true&espelho=true&inteiroTeor=true&textoPesquisa={termo.replace(' ', '%20')}"
        
        try:
            self.driver.get(url)
            logger.info("   Aguardando carregamento da página...")
            
            # Aguardar resultados carregarem
            time.sleep(5)  # Tempo para Angular carregar
            
            # Tentar encontrar cards de resultados
            # Precisamos inspecionar o HTML real do site para saber os seletores corretos
            
            # Possíveis seletores (ajustar após inspeção)
            selectors = [
                "//div[contains(@class, 'resultado')]",
                "//div[contains(@class, 'card')]",
                "//article",
                "//div[contains(@class, 'item')]",
                "//*[contains(text(), 'Processo:')]/ancestor::div[3]",
            ]
            
            cards_encontrados = []
            for selector in selectors:
                try:
                    cards = self.driver.find_elements(By.XPATH, selector)
                    if cards:
                        logger.info(f"   ✅ Encontrados {len(cards)} elementos com seletor: {selector[:50]}")
                        cards_encontrados = cards
                        break
                except:
                    continue
            
            if not cards_encontrados:
                # Pegar todo o texto da página para debug
                page_text = self.driver.find_element(By.TAG_NAME, 'body').text
                logger.warning(f"   ⚠️  Nenhum card encontrado. Texto da página:")
                logger.warning(page_text[:500])
                return []
            
            # Processar cada card
            for idx, card in enumerate(cards_encontrados[:limite]):
                if idx >= limite:
                    break
                
                try:
                    texto = card.text
                    
                    # Verificar se contém os termos de busca
                    if 'fornecimento' not in texto.lower():
                        continue
                    
                    # Extrair informações
                    resultado = self._extrair_info_card(texto, termo)
                    
                    if resultado:
                        self.resultados.append(resultado)
                        logger.info(f"   ✅ [{len(self.resultados)}] Processo: {resultado.get('numero_processo', 'N/A')}")
                
                except Exception as e:
                    logger.error(f"   ❌ Erro ao processar card {idx}: {e}")
                    continue
            
            logger.info(f"✅ Total coletado: {len(self.resultados)}")
            
        except Exception as e:
            logger.error(f"❌ Erro na busca: {e}")
        
        return self.resultados
    
    def _extrair_info_card(self, texto: str, termo: str) -> Optional[Dict]:
        """Extrai informações de um card"""
        
        # Número do processo
        match_processo = re.search(r'(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})', texto)
        numero_processo = match_processo.group(1) if match_processo else None
        
        if not numero_processo:
            return None
        
        # Relator
        match_relator = re.search(r'Relator(?:\(a\))?[:\s]+([A-ZÁÉÍÓÚ][A-ZÁÉÍÓÚa-záéíóúâãôêç\s]+?)(?:\n|5ª|[0-9]|TURMA)', texto)
        relator = match_relator.group(1).strip() if match_relator else None
        
        # Medicamento
        medicamento = extrair_nome_medicamento(texto)
        
        # Decisão
        match_decisao = re.search(r'Decisão[:\s]+(.*?)(?:\n\n|\Z)', texto, re.DOTALL)
        decisao = ' '.join(match_decisao.group(1).split()) if match_decisao else None
        
        return {
            'numero_processo': numero_processo,
            'relator': relator,
            'medicamento': medicamento,
            'decisao': decisao,
            'termo_busca': termo,
            'data_coleta': datetime.now().isoformat()
        }
    
    def salvar_screenshot(self, nome: str = "screenshot.png"):
        """Salva screenshot da página para debug"""
        self.driver.save_screenshot(nome)
        logger.info(f"📸 Screenshot salvo: {nome}")
    
    def fechar(self):
        """Fecha o navegador"""
        if self.driver:
            self.driver.quit()
            logger.info("🔒 Navegador fechado")
    
    def salvar_resultados(self, arquivo_csv: str = "tjdft_medicamentos.csv"):
        """Salva resultados em CSV"""
        if not self.resultados:
            logger.warning("⚠️  Nenhum resultado para salvar")
            return
        
        df = pd.DataFrame(self.resultados)
        df = df.drop_duplicates(subset=['numero_processo'], keep='first')
        df.to_csv(arquivo_csv, index=False, encoding='utf-8')
        
        logger.info(f"\n💾 Dados salvos: {arquivo_csv}")
        logger.info(f"📊 Total: {len(df)} processos únicos")
        logger.info(f"   Com relator: {df['relator'].notna().sum()}")
        logger.info(f"   Com medicamento: {df['medicamento'].notna().sum()}")
        logger.info(f"   Com decisão: {df['decisao'].notna().sum()}")
        
        return df


# ==================== EXECUÇÃO ====================

def main():
    """Função principal"""
    scraper = None
    
    try:
        scraper = ScraperTJDFTSelenium(headless=True)
        
        # Buscar pelos termos
        termos = [
            "fornecimento de medicamento",
            "fornecimento de medicação"
        ]
        
        for termo in termos:
            scraper.buscar_processos(termo, limite=250)
            time.sleep(3)
        
        # Salvar screenshot para debug
        scraper.salvar_screenshot("tjdft_debug.png")
        
        # Salvar resultados
        df = scraper.salvar_resultados()
        
        # Mostrar amostra
        if df is not None and not df.empty:
            print("\n" + "="*60)
            print("📋 AMOSTRA (primeiros 5):")
            print("="*60)
            for idx, row in df.head().iterrows():
                print(f"\n{idx+1}. {row['numero_processo']}")
                print(f"   Relator: {row['relator']}")
                print(f"   Medicamento: {row['medicamento']}")
                print(f"   Decisão: {row['decisao'][:60]}..." if row['decisao'] else "   Decisão: N/A")
    
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        if scraper:
            scraper.fechar()


if __name__ == "__main__":
    main()
