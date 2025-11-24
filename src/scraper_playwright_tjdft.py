"""
Scraper Automatizado para TJDFT usando Playwright
Coleta automática de acórdãos sobre fornecimento de medicamentos
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import pandas as pd
import time
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional
import json

# Tentar importar validador Gemini
try:
    from src.validador_gemini import ValidadorGemini

    VALIDADOR_DISPONIVEL = True
except ImportError:
    try:
        from validador_gemini import ValidadorGemini

        VALIDADOR_DISPONIVEL = True
    except ImportError:
        VALIDADOR_DISPONIVEL = False
        logger = logging.getLogger(__name__)
        logger.warning(
            "⚠️  validador_gemini não disponível. Instale: pip install google-generativeai"
        )

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            f'scraping_playwright_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# ==================== CONFIGURAÇÕES ====================

BASE_URL = "https://jurisdf.tjdft.jus.br/resultado"
TERMOS_BUSCA = ["fornecimento de medicação", "fornecimento de medicamento"]

DELAY_ENTRE_PAGINAS = 3  # segundos
DELAY_APOS_SCROLL = 2
TIMEOUT_PAGINA = 30000  # 30 segundos


# ==================== FUNÇÕES DE EXTRAÇÃO ====================


def extrair_nome_medicamento(texto: str) -> Optional[str]:
    """Extrai nome de medicamento do texto."""
    if not texto:
        return None

    # Lista expandida de exclusões (nomes comuns de relatores e termos jurídicos)
    exclusoes = {
        "APELAÇÃO",
        "RECURSO",
        "DECISÃO",
        "SENTENÇA",
        "TRIBUNAL",
        "PLANO",
        "SAÚDE",
        "FORNECIMENTO",
        "CÍVEL",
        "CRIMINAL",
        "TURMA",
        "ACÓRDÃO",
        "PROCESSO",
        "EMENTA",
        "CONHECIDO",
        "PROVIDO",
        "IMPROVIDO",
        "PARCIAL",
        "ANS",
        "SUS",
        "INAS",
        "ROL",
        "CDC",
        "COMARCA",
        "INSTÂNCIA",
        "RELATORA",
        "RELATOR",
        "JULGAMENTO",
        "UNÂNIME",
        "UNANIME",
        "NEGATIVA",
        "COBERTURA",
        # Nomes comuns de relatores/juízes
        "LUCIMEIRE",
        "MARIA",
        "SILVA",
        "ROBSON",
        "BARBOSA",
        "AZEVEDO",
        "ANA",
        "CANTARINO",
        "JANSEN",
        "FIALHO",
        "ALMEIDA",
        "FÁBIO",
        "EDUARDO",
        "MARQUES",
        "ALFEU",
        "MACHADO",
        "ALVARO",
        "CIARLINI",
        "ANGELO",
        "PASSARELI",
        "SIMONE",
        "LUCINDO",
        "GETÚLIO",
        "MORAES",
        "CARLOS",
        "RODRIGUES",
        "SARA",
        "MARTINS",
        "SANDOVAL",
        "OLIVEIRA",
    }

    # Padrão 1: Procurar após "medicamento", "fármaco", etc.
    padroes_contexto = [
        r"medicamento[s]?\s+(?:denominado|chamado|conhecido\s+como)?\s*[:\-]?\s*([A-ZÁÉÍÓÚÂÃÔÊ][a-záéíóúâãôêç]+)",
        r"fármaco[s]?\s+(?:denominado|chamado)?\s*[:\-]?\s*([A-ZÁÉÍÓÚÂÃÔÊ][a-záéíóúâãôêç]+)",
        r"remédio[s]?\s+(?:denominado|chamado)?\s*[:\-]?\s*([A-ZÁÉÍÓÚÂÃÔÊ][a-záéíóúâãôêç]+)",
        r"(?:uso|fornecimento|prescrição)\s+(?:do|de|da)\s+([A-ZÁÉÍÓÚÂÃÔÊ][a-záéíóúâãôêç]{4,})",
    ]

    for padrao in padroes_contexto:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            medicamento = match.group(1).strip().upper()
            if medicamento not in exclusoes and len(medicamento) > 3:
                return medicamento

    # Padrão 2: Palavras em maiúsculas no contexto de ementa (mais restritivo)
    # Apenas se estiver claramente no contexto médico
    if "MEDICAMENTO" in texto or "FORNECIMENTO" in texto:
        palavras_maiusculas = re.findall(r"\b([A-ZÁÉÍÓÚÂÃÔÊ]{5,})\b", texto)
        for palavra in palavras_maiusculas:
            if palavra not in exclusoes:
                return palavra

    return None


def extrair_dados_card(texto: str) -> Optional[Dict]:
    """Extrai informações estruturadas de um card de resultado."""

    # Número do processo
    match_processo = re.search(r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})", texto)
    numero_processo = match_processo.group(1) if match_processo else None

    if not numero_processo:
        return None

    # Relator
    match_relator = re.search(
        r"Relator(?:\(a\))?[:\s]+([A-ZÁÉÍÓÚ][A-ZÁÉÍÓÚa-záéíóúâãôêç\s]+?)(?:\n|5ª|[0-9]|TURMA|$)",
        texto,
        re.IGNORECASE,
    )
    relator = match_relator.group(1).strip() if match_relator else None

    # Medicamento
    medicamento = extrair_nome_medicamento(texto)

    # Decisão
    match_decisao = re.search(
        r"Decisão[:\s]+(.*?)(?:\n\n|\Z)", texto, re.DOTALL | re.IGNORECASE
    )
    decisao = " ".join(match_decisao.group(1).split()) if match_decisao else None

    # Ementa
    match_ementa = re.search(
        r"Ementa[:\s]+(.*?)(?:\n\n|Decisão:|$)", texto, re.DOTALL | re.IGNORECASE
    )
    ementa = match_ementa.group(1).strip()[:500] if match_ementa else None

    return {
        "numero_processo": numero_processo,
        "relator": relator,
        "medicamento": medicamento,
        "decisao": decisao,
        "ementa": ementa,
        "texto_completo": texto[:2000],  # Primeiros 2000 chars
        "data_coleta": datetime.now().isoformat(),
    }


# ==================== SCRAPER PLAYWRIGHT ====================


class ScraperPlaywright:
    """Scraper automatizado usando Playwright"""

    def __init__(
        self,
        headless: bool = False,
        usar_validador: bool = True,
        checkpoint_file: str = "data/raw/checkpoint.json",
    ):
        """
        Inicializa o scraper.

        Args:
            headless: Se False, mostra o navegador (útil para debug)
            usar_validador: Se True, usa Gemini para validar dados extraídos
            checkpoint_file: Arquivo para salvar progresso
        """
        self.headless = headless
        self.resultados = []
        self.playwright = None
        self.browser = None
        self.page = None
        self.checkpoint_file = checkpoint_file
        self.proximo_id = 1  # ID sequencial para os registros

        # Tentar carregar checkpoint existente
        self._carregar_checkpoint()

        # Inicializar validador Gemini se disponível
        self.validador = None
        if usar_validador and VALIDADOR_DISPONIVEL:
            try:
                self.validador = ValidadorGemini()
                if self.validador.habilitado:
                    logger.info("✅ Validador Gemini habilitado")
                else:
                    logger.info(
                        "ℹ️  Validador Gemini desabilitado (API key não encontrada)"
                    )
            except Exception as e:
                logger.warning(f"⚠️  Erro ao inicializar validador: {e}")
                self.validador = None

    def _carregar_checkpoint(self):
        """Carrega checkpoint de execução anterior se existir"""
        try:
            import os

            if os.path.exists(self.checkpoint_file):
                with open(self.checkpoint_file, "r", encoding="utf-8") as f:
                    checkpoint = json.load(f)
                    self.resultados = checkpoint.get("resultados", [])
                    self.proximo_id = checkpoint.get("proximo_id", 1)
                    logger.info(
                        f"📂 Checkpoint carregado: {len(self.resultados)} processos, próximo ID: {self.proximo_id}"
                    )
        except Exception as e:
            logger.warning(f"⚠️  Erro ao carregar checkpoint: {e}")
            self.resultados = []
            self.proximo_id = 1

    def _salvar_checkpoint(self):
        """Salva checkpoint do progresso atual"""
        try:
            import os

            os.makedirs(os.path.dirname(self.checkpoint_file), exist_ok=True)

            checkpoint = {
                "resultados": self.resultados,
                "proximo_id": self.proximo_id,
                "total_processos": len(self.resultados),
                "ultima_atualizacao": datetime.now().isoformat(),
            }

            with open(self.checkpoint_file, "w", encoding="utf-8") as f:
                json.dump(checkpoint, f, ensure_ascii=False, indent=2)

            logger.debug(f"💾 Checkpoint salvo: {len(self.resultados)} processos")
        except Exception as e:
            logger.warning(f"⚠️  Erro ao salvar checkpoint: {e}")

    def iniciar(self):
        """Inicializa o navegador Playwright"""
        logger.info("🚀 Inicializando Playwright...")

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=["--disable-blink-features=AutomationControlled"],
        )

        context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        )

        self.page = context.new_page()
        logger.info("✅ Navegador iniciado")

    def buscar_termo(self, termo: str, limite: int = 500) -> List[Dict]:
        """
        Busca processos por termo específico.

        Args:
            termo: Termo de busca
            limite: Número máximo de resultados
        """
        logger.info(f"🔍 Buscando por: '{termo}'")

        # Construir URL com query string
        url = f"{BASE_URL}?sinonimos=true&espelho=true&inteiroTeor=true&textoPesquisa={termo.replace(' ', '%20')}"

        # Codificar caracteres especiais (ç -> %C3%A7)
        url = url.replace("ç", "%C3%A7").replace("ã", "%C3%A3")

        try:
            # Navegar para a página
            logger.info(f"   Acessando: {url}")
            self.page.goto(url, wait_until="networkidle", timeout=TIMEOUT_PAGINA)

            # Aguardar carregamento inicial
            logger.info("   Aguardando carregamento...")
            time.sleep(5)

            # Tentar aguardar por elementos de resultado
            try:
                self.page.wait_for_selector(
                    '[class*="resultado"], article, mat-card', timeout=10000
                )
            except PlaywrightTimeout:
                logger.warning(
                    "   ⚠️  Timeout aguardando seletor específico, continuando..."
                )

            pagina_atual = 1
            processos_coletados = len(self.resultados)

            while processos_coletados < limite:
                logger.info(
                    f"   📄 Página {pagina_atual} - Coletados: {processos_coletados}/{limite}"
                )

                # Scroll para carregar conteúdo dinâmico
                self._scroll_pagina()

                # Extrair dados da página atual (com limite dinâmico)
                novos = self._extrair_dados_pagina(
                    termo, limite_restante=limite - processos_coletados
                )
                processos_coletados = len(self.resultados)

                logger.info(
                    f"      ✅ Extraídos {len(novos)} processos desta página (total: {processos_coletados})"
                )

                if processos_coletados >= limite:
                    logger.info(f"   ✅ Limite de {limite} processos atingido!")
                    break

                # Tentar ir para próxima página
                if not self._proxima_pagina():
                    logger.info("   ℹ️  Não há mais páginas disponíveis")
                    break

                pagina_atual += 1
                time.sleep(DELAY_ENTRE_PAGINAS)

            logger.info(f"✅ Total coletado para '{termo}': {processos_coletados}")

        except Exception as e:
            logger.error(f"❌ Erro na busca: {e}")
            import traceback

            traceback.print_exc()

        return self.resultados

    def _scroll_pagina(self):
        """Faz scroll na página para carregar conteúdo lazy-load"""
        try:
            # Scroll suave até o final
            self.page.evaluate(
                """
                () => {
                    window.scrollTo({
                        top: document.body.scrollHeight,
                        behavior: 'smooth'
                    });
                }
            """
            )
            time.sleep(DELAY_APOS_SCROLL)

            # Voltar ao topo
            self.page.evaluate("() => window.scrollTo(0, 0)")
        except Exception as e:
            logger.warning(f"   ⚠️  Erro no scroll: {e}")

    def _extrair_dados_pagina(
        self, termo: str, limite_restante: int = 999
    ) -> List[Dict]:
        """Extrai dados de todos os cards da página atual clicando em Detalhes"""
        novos_resultados = []

        try:
            # Aguardar botões de detalhes estarem visíveis
            logger.info("      ⏳ Aguardando botões 'Detalhes' ficarem visíveis...")
            try:
                self.page.wait_for_selector(
                    'button:has-text("Detalhes")', timeout=10000
                )
            except PlaywrightTimeout:
                logger.warning("      ⚠️  Timeout aguardando botões Detalhes")
                return novos_resultados

            time.sleep(2)

            # Primeiro, extrair todos os números de processos visíveis na página
            texto_lista = self.page.inner_text("body")
            processos_visiveis = re.findall(
                r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})", texto_lista
            )

            # Obter todos os botões "Detalhes"
            botoes_detalhes = self.page.query_selector_all(
                'button:has-text("Detalhes")'
            )
            total_botoes = len(botoes_detalhes)

            logger.info(f"      🔍 Encontrados {total_botoes} processos na página")

            # Limitar ao menor valor entre: total de botões, 20, ou limite restante
            processos_para_coletar = min(total_botoes, 20, limite_restante)

            for idx in range(processos_para_coletar):
                try:
                    # Identificar qual processo esperamos (baseado na lista visível)
                    processo_esperado = (
                        processos_visiveis[idx]
                        if idx < len(processos_visiveis)
                        else None
                    )

                    # Re-query os botões a cada iteração (DOM pode mudar)
                    botoes = self.page.query_selector_all('button:has-text("Detalhes")')
                    if idx >= len(botoes):
                        break

                    botao = botoes[idx]

                    # Scroll até o botão para garantir que está visível
                    try:
                        botao.scroll_into_view_if_needed()
                    except:
                        pass

                    time.sleep(0.5)

                    # Clicar no botão Detalhes
                    logger.info(
                        f"      🖱️  Clicando em Detalhes [{idx+1}/{processos_para_coletar}] - Esperado: {processo_esperado}..."
                    )
                    botao.click()

                    # Aguardar modal abrir
                    time.sleep(2)

                    # Extrair dados do modal de detalhes
                    dados = self._extrair_dados_modal(
                        termo, numero_processo_esperado=processo_esperado
                    )

                    if dados and dados["numero_processo"]:
                        # Validar com Gemini se disponível
                        if self.validador and self.validador.habilitado:
                            validacao = self.validador.validar_processo(
                                numero_processo=dados["numero_processo"],
                                relator=dados.get("relator", ""),
                                medicamento=dados.get("medicamento", ""),
                                decisao=dados.get("decisao", ""),
                                texto_completo=dados.get(
                                    "texto_completo", ""
                                ),  # Passa texto completo!
                            )

                            # Adicionar campos de validação e extração aos dados
                            dados["genero_relator"] = validacao.get(
                                "genero_relator", "Indeterminado"
                            )
                            dados["confianca_genero"] = validacao.get(
                                "confianca_genero", 0
                            )

                            dados["medicamento_validado"] = validacao.get(
                                "medicamento_valido", None
                            )

                            # Se a IA extraiu uma decisão melhor, usa ela
                            decisao_extraida = validacao.get("decisao_extraida", "")
                            if decisao_extraida and (
                                not dados.get("decisao")
                                or len(decisao_extraida) > len(dados.get("decisao", ""))
                            ):
                                dados["decisao_extraida_ia"] = decisao_extraida

                            dados["decisao_favoravel"] = validacao.get(
                                "decisao_favoravel", None
                            )
                            dados["observacoes_validacao"] = validacao.get(
                                "observacoes", ""
                            )

                        # Verificar duplicatas
                        if not any(
                            r["numero_processo"] == dados["numero_processo"]
                            for r in self.resultados
                        ):
                            # FILTRO: Ignorar processos sem medicamento válido
                            medicamento = dados.get("medicamento")

                            # Verificar se tem medicamento
                            if not medicamento or medicamento.strip() == "":
                                logger.info(
                                    f"         ⏭️  Processo {dados['numero_processo']} ignorado: sem medicamento"
                                )
                                continue

                            # Verificar se é apenas "MEDICAÇÃO" (muito genérico)
                            medicamento_upper = medicamento.upper().strip()
                            termos_genericos = [
                                "MEDICAÇÃO",
                                "MEDICACAO",
                                "MEDICAMENTO",
                                "MEDICAMENTOS",
                                "REMÉDIO",
                                "REMEDIO",
                                "FÁRMACO",
                                "FARMACO",
                                "PRESCRITO",
                                "REGISTRADO",
                                "PRODUTO",
                            ]

                            if medicamento_upper in termos_genericos:
                                logger.info(
                                    f"         ⏭️  Processo {dados['numero_processo']} ignorado: medicamento genérico '{medicamento}'"
                                )
                                continue

                            # Adicionar ID sequencial
                            dados["id"] = self.proximo_id
                            self.proximo_id += 1

                            self.resultados.append(dados)
                            novos_resultados.append(dados)

                            # Salvar checkpoint a cada 5 processos
                            if len(self.resultados) % 5 == 0:
                                self._salvar_checkpoint()

                            # Log com informações de validação
                            med_info = dados.get("medicamento", "N/A")
                            if dados.get("medicamento_sugerido"):
                                med_info = (
                                    f"{med_info} → {dados['medicamento_sugerido']}"
                                )

                            genero_info = ""
                            if "genero_relator" in dados:
                                genero_info = f" [{dados['genero_relator']}]"

                            logger.info(
                                f"         ✅ [{dados['id']}] {dados['numero_processo']}{genero_info} - {med_info}"
                            )
                        else:
                            logger.info(
                                f"         ⚠️  Processo {dados['numero_processo']} já coletado (duplicata)"
                            )

                    # Fechar modal
                    self._fechar_modal()
                    time.sleep(0.8)

                except KeyboardInterrupt:
                    logger.info("      ⚠️  Interrompido pelo usuário")
                    raise
                except Exception as e:
                    logger.warning(f"      ⚠️  Erro no processo {idx+1}: {e}")
                    # Tentar fechar modal se houver erro
                    self._fechar_modal()
                    continue

        except KeyboardInterrupt:
            logger.info("   ⚠️  Coleta interrompida pelo usuário")
            raise
        except Exception as e:
            logger.error(f"   ❌ Erro na extração: {e}")
            import traceback

            traceback.print_exc()

        return novos_resultados

    def _extrair_dados_modal(
        self, termo: str, numero_processo_esperado: Optional[str] = None
    ) -> Optional[Dict]:
        """Extrai dados do modal de detalhes aberto"""
        try:
            # Aguardar conteúdo do modal carregar completamente
            logger.info("         ⏳ Aguardando modal carregar...")
            time.sleep(3)  # Tempo maior para garantir carregamento

            # Pegar todo o texto da página (o modal é renderizado no body)
            texto_completo = self.page.inner_text("body")

            logger.info(f"         📄 Capturado {len(texto_completo)} chars")

            # Se sabemos qual processo esperamos, procurar especificamente por ele
            if numero_processo_esperado:
                # Procurar pelo processo esperado
                idx_esperado = texto_completo.find(numero_processo_esperado)
                if idx_esperado == -1:
                    logger.warning(
                        f"         ⚠️  Processo esperado {numero_processo_esperado} não encontrado"
                    )
                    return None

                numero_processo = numero_processo_esperado
                inicio = idx_esperado
            else:
                # Procurar pelo primeiro processo (fallback)
                match_processo = re.search(
                    r"(\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})", texto_completo
                )
                if not match_processo:
                    logger.warning(
                        "         ⚠️  Número do processo não encontrado no texto"
                    )
                    return None

                numero_processo = match_processo.group(1)
                inicio = match_processo.start()

            # Extrair bloco de texto próximo ao número do processo (próximos 5000 chars)
            texto_processo = texto_completo[
                max(0, inicio - 200) : min(len(texto_completo), inicio + 5000)
            ]

            # Relator
            match_relator = re.search(
                r"Relator(?:\(a\))?[:\s]+([A-ZÁÉÍÓÚ][A-ZÁÉÍÓÚa-záéíóúâãôêç\s]+?)(?:\n|maps_home|5ª|[0-9]|TURMA|gavel|$)",
                texto_processo,
                re.IGNORECASE,
            )
            relator = match_relator.group(1).strip() if match_relator else None

            # Medicamento
            medicamento = extrair_nome_medicamento(texto_processo)

            # Decisão - procurar pelo padrão "Decisão:" seguido do texto completo
            decisao = None

            # Padrão 1: Procurar por "Decisão:" explícito
            match_decisao = re.search(
                r"Decisão:\s*\n?\s*(.+?)(?=\n(?:remove|add|Detalhes|Acórdão:|Processo:)|$)",
                texto_processo,
                re.IGNORECASE | re.DOTALL,
            )
            if match_decisao:
                decisao = " ".join(match_decisao.group(1).split()).strip()

            # Padrão 2: Se não achou, procurar por linhas com palavras-chave de decisão
            if not decisao:
                linhas = texto_processo.split("\n")
                for i, linha in enumerate(linhas):
                    linha_upper = linha.upper()
                    if any(
                        palavra in linha_upper
                        for palavra in [
                            "CONHECER",
                            "NEGAR PROVIMENTO",
                            "DAR PROVIMENTO",
                            "DESPROVIDO",
                            "PROVIDO",
                            "NEGOU",
                            "DEU",
                            "UNÂNIME",
                            "UNANIME",
                        ]
                    ):
                        # Pegar essa linha e as próximas até encontrar uma linha vazia ou outro delimitador
                        decisao_linhas = [linha]
                        for j in range(i + 1, min(len(linhas), i + 5)):
                            proxima = linhas[j].strip()
                            if (
                                not proxima
                                or proxima.startswith("remove")
                                or proxima.startswith("add")
                                or proxima.startswith("Detalhes")
                            ):
                                break
                            if any(
                                palavra in proxima.upper()
                                for palavra in [
                                    "CONHECER",
                                    "NEGAR",
                                    "DAR",
                                    "PROVIMENTO",
                                    "PROVIDO",
                                    "IMPROVIDO",
                                    "DESPROVIDO",
                                    "UNÂNIME",
                                    "UNANIME",
                                    "MAIORIA",
                                ]
                            ):
                                decisao_linhas.append(proxima)
                        decisao = " ".join(decisao_linhas).strip()
                        break

            return {
                "numero_processo": numero_processo,
                "relator": relator,
                "medicamento": medicamento,
                "decisao": decisao,
                "texto_completo": texto_processo[:3000],  # Reduzido
                "data_coleta": datetime.now().isoformat(),
                "termo_busca": termo,
            }

        except Exception as e:
            logger.warning(f"         ⚠️  Erro ao extrair dados do modal: {e}")
            import traceback

            traceback.print_exc()
            return None

    def _fechar_modal(self):
        """Fecha o modal de detalhes se estiver aberto"""
        try:
            # Tentar diferentes formas de fechar
            seletores_fechar = [
                'button:has-text("FECHAR")',
                'button:has-text("Fechar")',
                'button:has-text("×")',
                'button:has-text("ESC")',
                '[aria-label*="fechar"]',
                '[aria-label*="close"]',
                "mat-dialog-container button[mat-dialog-close]",
                ".close-button",
            ]

            for seletor in seletores_fechar:
                try:
                    botao = self.page.query_selector(seletor)
                    if botao:
                        botao.click()
                        time.sleep(0.3)
                        return True
                except:
                    continue

            # Se não achou botão, tentar ESC
            self.page.keyboard.press("Escape")
            time.sleep(0.3)

        except Exception as e:
            logger.warning(f"         ⚠️  Erro ao fechar modal: {e}")
            # Tentar ESC como último recurso
            try:
                self.page.keyboard.press("Escape")
            except:
                pass

    def _proxima_pagina(self) -> bool:
        """Tenta navegar para a próxima página de resultados"""
        try:
            # Aguardar um pouco antes de procurar botão
            time.sleep(2)

            # Seletores específicos para o TJDFT (baseado em teste real)
            seletores = [
                'button:has-text("navigate_next")',  # TJDFT usa Material Icons
                'button:has-text("keyboard_arrow_right")',
                'button[aria-label="Next page"]',
                'button[aria-label="Próxima página"]',
                ".mat-paginator-navigation-next:not([disabled])",
                "button.mat-paginator-navigation-next:not([disabled])",
                'button:has-text("›"):not([disabled])',
            ]

            for seletor in seletores:
                try:
                    botoes = self.page.query_selector_all(seletor)
                    if botoes:
                        # TJDFT pode ter múltiplos botões navigate_next, pegar o último
                        botao = botoes[-1] if len(botoes) > 1 else botoes[0]

                        # Verificar se não está desabilitado
                        disabled = botao.get_attribute("disabled")
                        aria_disabled = botao.get_attribute("aria-disabled")

                        if disabled is None and aria_disabled != "true":
                            logger.info(f"      🔍 Clicando botão: {seletor}")
                            botao.click()
                            time.sleep(4)  # Aguardar página carregar
                            logger.info("      ➡️  Navegou para próxima página")
                            return True
                        else:
                            logger.info(f"      ⚠️  Botão '{seletor}' está desabilitado")
                except Exception as e:
                    logger.debug(f"      ⚠️  Seletor '{seletor}' falhou: {e}")
                    continue

            logger.info("      ℹ️  Nenhum botão de próxima página encontrado/habilitado")
            return False

        except Exception as e:
            logger.warning(f"   ⚠️  Erro ao tentar próxima página: {e}")
            return False

    def coletar_multiplos_termos(
        self, termos: List[str], limite_por_termo: int = 250
    ) -> pd.DataFrame:
        """
        Coleta dados para múltiplos termos de busca.

        Args:
            termos: Lista de termos para buscar
            limite_por_termo: Número máximo de resultados por termo
        """
        logger.info("=" * 60)
        logger.info("🚀 INICIANDO COLETA AUTOMATIZADA - PLAYWRIGHT")
        logger.info("=" * 60)

        self.iniciar()

        try:
            for termo in termos:
                self.buscar_termo(termo, limite=limite_por_termo)
        finally:
            self.fechar()

        # Criar DataFrame e remover duplicatas
        df = pd.DataFrame(self.resultados)
        if not df.empty:
            df = df.drop_duplicates(subset=["numero_processo"], keep="first")

        logger.info("=" * 60)
        logger.info(f"✅ COLETA FINALIZADA: {len(df)} processos únicos")
        logger.info("=" * 60)

        return df

    def salvar_screenshot(self, nome: str = "screenshot_playwright.png"):
        """Salva screenshot da página atual"""
        if self.page:
            self.page.screenshot(path=nome, full_page=True)
            logger.info(f"📸 Screenshot salvo: {nome}")

    def fechar(self):
        """Fecha o navegador"""
        try:
            if self.browser:
                self.browser.close()
        except Exception:
            pass  # Já fechado

        try:
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass  # Já parado

        logger.info("🔒 Navegador fechado")

    def salvar_resultados(
        self,
        arquivo_csv: str = "tjdft_medicamentos_playwright.csv",
        arquivo_json: str = "tjdft_medicamentos_playwright.json",
    ):
        """Salva resultados em arquivos"""
        if not self.resultados:
            logger.warning("⚠️  Nenhum resultado para salvar")
            return None

        df = pd.DataFrame(self.resultados)
        df = df.drop_duplicates(subset=["numero_processo"], keep="first")

        # Reorganizar colunas na ordem solicitada (ID primeiro)
        colunas_ordenadas = [
            "id",
            "numero_processo",
            "relator",
            "genero_relator",
            "confianca_genero",
            "medicamento",
            "medicamento_validado",
            "decisao_favoravel",
            "decisao",
            "decisao_extraida_ia",
            "observacoes_validacao",
            "termo_busca",
            "data_coleta",
            "texto_completo",
        ]

        # Manter apenas colunas que existem no DataFrame
        colunas_existentes = [col for col in colunas_ordenadas if col in df.columns]

        # Adicionar colunas extras que não estão na lista ordenada (se houver)
        colunas_extras = [col for col in df.columns if col not in colunas_ordenadas]

        # Reordenar DataFrame
        df = df[colunas_existentes + colunas_extras]

        # Salvar CSV
        df.to_csv(arquivo_csv, index=False, encoding="utf-8")
        logger.info(f"💾 CSV salvo: {arquivo_csv}")

        # Salvar JSON
        df.to_json(arquivo_json, orient="records", indent=2, force_ascii=False)
        logger.info(f"💾 JSON salvo: {arquivo_json}")

        # Salvar checkpoint final
        self._salvar_checkpoint()
        logger.info(f"💾 Checkpoint final salvo: {self.checkpoint_file}")

        # Estatísticas
        logger.info("\n📊 ESTATÍSTICAS:")
        logger.info(f"   Total de processos: {len(df)}")
        logger.info(f"   Processos com relator: {df['relator'].notna().sum()}")
        logger.info(f"   Processos com medicamento: {df['medicamento'].notna().sum()}")
        logger.info(f"   Processos com decisão: {df['decisao'].notna().sum()}")

        if df["relator"].notna().sum() > 0:
            logger.info(f"\n   Top 5 Relatores:")
            for relator, count in df["relator"].value_counts().head(5).items():
                logger.info(f"      {relator}: {count}")

        if df["medicamento"].notna().sum() > 0:
            logger.info(f"\n   Top 5 Medicamentos:")
            for med, count in df["medicamento"].value_counts().head(5).items():
                logger.info(f"      {med}: {count}")

        return df


# ==================== EXECUÇÃO ====================


def main():
    """Função principal"""
    scraper = ScraperPlaywright(
        headless=True,  # headless=True para executar em background
        usar_validador=False,  # Desabilitar Gemini (quota excedida)
    )

    try:
        # Coletar dados
        df = scraper.coletar_multiplos_termos(
            termos=TERMOS_BUSCA, limite_por_termo=375  # 375 de cada termo = ~750 total
        )

        # Salvar resultados
        scraper.salvar_resultados()

        # Mostrar amostra
        if not df.empty:
            print("\n" + "=" * 60)
            print("📋 AMOSTRA DOS DADOS (primeiros 5):")
            print("=" * 60)
            for idx, row in df.head().iterrows():
                print(f"\n{idx+1}. Processo: {row['numero_processo']}")
                print(f"   Relator: {row['relator']}")
                print(f"   Medicamento: {row['medicamento']}")
                decisao = (
                    row["decisao"][:80] + "..."
                    if row["decisao"] and len(row["decisao"]) > 80
                    else row["decisao"]
                )
                print(f"   Decisão: {decisao}")

        return df

    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        import traceback

        traceback.print_exc()

    finally:
        if scraper:
            scraper.fechar()


if __name__ == "__main__":
    main()
