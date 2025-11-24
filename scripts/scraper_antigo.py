"""
Scraper para coleta de decisões judiciais sobre fornecimento de medicamentos - TJDFT
Projeto: Análise de viés de gênero em sentenças judiciais
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional
import json

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'scraping_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ==================== CONFIGURAÇÕES ====================

BASE_URL = "https://jurisdf.tjdft.jus.br"
SEARCH_URL = f"{BASE_URL}/resultado"

# Termos de busca
TERMOS_BUSCA = [
    "fornecimento de medicamento",
    "fornecimento de medicação"
]

# Delay entre requisições (respeitar o servidor)
DELAY_ENTRE_REQUISICOES = 2  # segundos
DELAY_ENTRE_PAGINAS = 3

# Headers para simular navegador
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
}


# ==================== FUNÇÕES AUXILIARES ====================

def extrair_nome_medicamento(texto: str) -> Optional[str]:
    """
    Extrai nome de medicamento do texto da ementa/decisão.
    Procura por palavras em maiúsculas ou após padrões comuns.
    """
    if not texto:
        return None
    
    # Padrões comuns
    padroes = [
        r'medicamento[:\s]+([A-ZÁÉÍÓÚÂÃÔÊ][a-záéíóúâãôêç]+(?:\s+[A-ZÁÉÍÓÚÂÃÔÊ][a-záéíóúâãôêç]+)?)',
        r'fármaco[:\s]+([A-ZÁÉÍÓÚÂÃÔÊ][a-záéíóúâãôêç]+)',
        r'remédio[:\s]+([A-ZÁÉÍÓÚÂÃÔÊ][a-záéíóúâãôêç]+)',
        r'\b([A-ZÁÉÍÓÚÂÃÔÊ]{3,}(?:\s+[A-ZÁÉÍÓÚÂÃÔÊ]{3,})?)\b',  # Palavras em maiúsculas
    ]
    
    for padrao in padroes:
        matches = re.findall(padrao, texto)
        if matches:
            # Retorna o primeiro medicamento encontrado
            medicamento = matches[0].strip()
            # Filtrar palavras comuns que não são medicamentos
            if medicamento.upper() not in ['APELAÇÃO', 'RECURSO', 'DECISÃO', 'SENTENÇA', 'TRIBUNAL', 'PLANO', 'SAÚDE', 'FORNECIMENTO']:
                return medicamento
    
    return None


def extrair_relator(texto: str) -> Optional[str]:
    """
    Extrai nome do relator do texto.
    """
    if not texto:
        return None
    
    padroes = [
        r'Relator(?:\(a\))?[:\s]+([A-ZÁÉÍÓÚÂÃÔÊ][A-ZÁÉÍÓÚÂÃÔÊa-záéíóúâãôêç\s]+?)(?:\n|$|5ª|[0-9])',
        r'RELATOR(?:\(A\))?[:\s]+([A-ZÁÉÍÓÚÂÃÔÊ][A-ZÁÉÍÓÚÂÃÔÊa-záéíóúâãôêç\s]+?)(?:\n|$|5ª|[0-9])',
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto)
        if match:
            return match.group(1).strip()
    
    return None


def extrair_decisao(texto: str) -> Optional[str]:
    """
    Extrai a decisão do processo.
    """
    if not texto:
        return None
    
    # Procurar por "Decisão:" seguido do texto
    match = re.search(r'Decisão[:\s]+(.*?)(?:\n\n|\n[A-Z]|$)', texto, re.DOTALL)
    if match:
        decisao = match.group(1).strip()
        # Limpar quebras de linha extras
        decisao = ' '.join(decisao.split())
        return decisao
    
    return None


def extrair_numero_processo(texto: str) -> Optional[str]:
    """
    Extrai número do processo no formato CNJ.
    """
    if not texto:
        return None
    
    # Formato: 0711915-93.2024.8.07.0001
    match = re.search(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', texto)
    if match:
        return match.group(0)
    
    return None


# ==================== SCRAPER PRINCIPAL ====================

class ScraperTJDFT:
    """
    Scraper para o site de jurisprudência do TJDFT
    """
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.resultados = []
        
    def buscar_processos(self, termo: str, limite: int = 500) -> List[Dict]:
        """
        Busca processos por termo e coleta informações.
        """
        logger.info(f"🔍 Buscando por: '{termo}'")
        
        # Parâmetros da busca
        params = {
            'sinonimos': 'true',
            'espelho': 'true',
            'inteiroTeor': 'true',
            'textoPesquisa': termo
        }
        
        pagina = 1
        processos_coletados = 0
        
        while processos_coletados < limite:
            try:
                logger.info(f"📄 Página {pagina} - Coletados: {processos_coletados}/{limite}")
                
                # Adicionar parâmetro de página se não for a primeira
                if pagina > 1:
                    params['pagina'] = str(pagina)
                
                response = self.session.get(SEARCH_URL, params=params, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Procurar cards de resultados
                cards = soup.find_all(['div', 'article'], class_=re.compile(r'resultado|card|item'))
                
                if not cards:
                    # Tentar estrutura alternativa
                    cards = soup.find_all(text=re.compile(r'Processo:\s*\d{7}-\d{2}'))
                    if cards:
                        # Se encontrou pelo texto, pegar o elemento pai
                        cards = [card.find_parent() for card in cards if card.find_parent()]
                
                if not cards:
                    logger.warning(f"⚠️  Nenhum resultado encontrado na página {pagina}")
                    break
                
                logger.info(f"   Encontrados {len(cards)} resultados nesta página")
                
                # Processar cada card
                for card in cards:
                    if processos_coletados >= limite:
                        break
                    
                    try:
                        # Extrair texto completo do card
                        texto_card = card.get_text(separator='\n', strip=True)
                        
                        # Verificar se contém os termos de busca
                        texto_lower = texto_card.lower()
                        if 'fornecimento' not in texto_lower or ('medicamento' not in texto_lower and 'medicação' not in texto_lower):
                            continue
                        
                        # Extrair informações
                        numero_processo = extrair_numero_processo(texto_card)
                        relator = extrair_relator(texto_card)
                        medicamento = extrair_nome_medicamento(texto_card)
                        decisao = extrair_decisao(texto_card)
                        
                        if numero_processo:
                            resultado = {
                                'numero_processo': numero_processo,
                                'relator': relator,
                                'medicamento': medicamento,
                                'decisao': decisao,
                                'termo_busca': termo,
                                'texto_completo': texto_card[:1000],  # Primeiros 1000 chars
                                'data_coleta': datetime.now().isoformat()
                            }
                            
                            self.resultados.append(resultado)
                            processos_coletados += 1
                            
                            logger.info(f"   ✅ Processo {numero_processo} - Relator: {relator}")
                    
                    except Exception as e:
                        logger.error(f"   ❌ Erro ao processar card: {e}")
                        continue
                
                # Verificar se há próxima página
                proxima = soup.find('a', text=re.compile(r'Próxima|>>|›'))
                if not proxima and processos_coletados < limite:
                    logger.info("   Não há mais páginas disponíveis")
                    break
                
                pagina += 1
                time.sleep(DELAY_ENTRE_PAGINAS)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Erro na requisição: {e}")
                break
            except Exception as e:
                logger.error(f"❌ Erro inesperado: {e}")
                break
        
        logger.info(f"✅ Total coletado para '{termo}': {processos_coletados}")
        return self.resultados
    
    def coletar_multiplos_termos(self, termos: List[str], limite_por_termo: int = 250) -> pd.DataFrame:
        """
        Coleta dados para múltiplos termos de busca.
        """
        logger.info("="*60)
        logger.info("🚀 INICIANDO COLETA - TJDFT MEDICAMENTOS")
        logger.info("="*60)
        
        for termo in termos:
            self.buscar_processos(termo, limite=limite_por_termo)
            time.sleep(DELAY_ENTRE_REQUISICOES)
        
        # Remover duplicatas por número de processo
        df = pd.DataFrame(self.resultados)
        if not df.empty:
            df = df.drop_duplicates(subset=['numero_processo'], keep='first')
        
        logger.info("="*60)
        logger.info(f"✅ COLETA FINALIZADA: {len(df)} processos únicos")
        logger.info("="*60)
        
        return df
    
    def salvar_resultados(self, df: pd.DataFrame, arquivo_csv: str = "tjdft_medicamentos.csv", 
                         arquivo_json: str = "tjdft_medicamentos.json"):
        """
        Salva resultados em CSV e JSON.
        """
        if df.empty:
            logger.warning("⚠️  Nenhum dado para salvar")
            return
        
        # Salvar CSV
        df.to_csv(arquivo_csv, index=False, encoding='utf-8')
        logger.info(f"💾 CSV salvo: {arquivo_csv}")
        
        # Salvar JSON
        df.to_json(arquivo_json, orient='records', indent=2, force_ascii=False)
        logger.info(f"💾 JSON salvo: {arquivo_json}")
        
        # Estatísticas
        logger.info("\n📊 ESTATÍSTICAS:")
        logger.info(f"   Total de processos: {len(df)}")
        logger.info(f"   Processos com relator identificado: {df['relator'].notna().sum()}")
        logger.info(f"   Processos com medicamento identificado: {df['medicamento'].notna().sum()}")
        logger.info(f"   Processos com decisão identificada: {df['decisao'].notna().sum()}")
        
        if df['relator'].notna().sum() > 0:
            logger.info(f"\n   Top 5 Relatores:")
            for relator, count in df['relator'].value_counts().head(5).items():
                logger.info(f"      {relator}: {count}")
        
        if df['medicamento'].notna().sum() > 0:
            logger.info(f"\n   Top 5 Medicamentos:")
            for med, count in df['medicamento'].value_counts().head(5).items():
                logger.info(f"      {med}: {count}")


# ==================== EXECUÇÃO ====================

def main():
    """
    Função principal para executar o scraper.
    """
    scraper = ScraperTJDFT()
    
    # Coletar dados
    df = scraper.coletar_multiplos_termos(
        termos=TERMOS_BUSCA,
        limite_por_termo=250  # 250 de cada termo = ~500 total
    )
    
    # Salvar resultados
    scraper.salvar_resultados(df)
    
    # Mostrar amostra
    if not df.empty:
        print("\n" + "="*60)
        print("📋 AMOSTRA DOS DADOS (primeiros 5 registros):")
        print("="*60)
        for idx, row in df.head().iterrows():
            print(f"\n{idx+1}. Processo: {row['numero_processo']}")
            print(f"   Relator: {row['relator']}")
            print(f"   Medicamento: {row['medicamento']}")
            print(f"   Decisão: {row['decisao'][:80]}..." if row['decisao'] else "   Decisão: N/A")
    
    return df


if __name__ == "__main__":
    main()
