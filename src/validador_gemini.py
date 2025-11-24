"""
Validador usando Google Gemini API (gratuita)
Para instalar: pip install google-generativeai
"""

import google.generativeai as genai
import os
import json
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ValidadorGemini:
    """Validador de dados usando Gemini API"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa o validador.

        Args:
            api_key: Chave da API Gemini. Se None, tenta ler de GEMINI_API_KEY
        """
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")

        if not self.api_key:
            logger.warning("⚠️  GEMINI_API_KEY não configurada. Validação desabilitada.")
            self.habilitado = False
            return

        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(
                "gemini-2.5-flash"
            )  # Modelo atualizado e gratuito
            self.habilitado = True
            logger.info("✅ Gemini API configurada")
        except Exception as e:
            logger.error(f"❌ Erro ao configurar Gemini: {e}")
            self.habilitado = False

    def validar_processo(
        self,
        numero_processo: str,
        relator: str,
        medicamento: str,
        decisao: str,
        texto_completo: str = "",
    ) -> Dict:
        """
        Valida e extrai dados de um processo judicial usando IA.
        A IA analisa o texto completo para extrair/validar informações.

        Args:
            numero_processo: Número do processo
            relator: Nome do relator (pode estar vazio, IA vai extrair)
            medicamento: Nome do medicamento (pode estar vazio, IA vai extrair)
            decisao: Texto da decisão (pode estar vazio, IA vai extrair)
            texto_completo: Texto completo do processo (IMPORTANTE!)

        Returns:
            Dict com validações e extrações: {
                'genero_relator': 'M' ou 'F' ou 'Indeterminado',
                'confianca_genero': 0-100,
                'medicamento_extraido': str (medicamento encontrado pela IA),
                'medicamento_valido': True/False,
                'decisao_extraida': str (decisão encontrada pela IA),
                'decisao_favoravel': True/False,
                'observacoes': str
            }
        """
        if not self.habilitado:
            return {
                "genero_relator": "Indeterminado",
                "confianca_genero": 0,
                "medicamento_extraido": medicamento or "",
                "medicamento_valido": None,
                "decisao_extraida": decisao or "",
                "decisao_favoravel": None,
                "observacoes": "Validação desabilitada (API não configurada)",
            }

        try:
            # Usar o texto completo se disponível, caso contrário usar os campos individuais
            texto_para_analise = (
                texto_completo[:5000]
                if texto_completo
                else f"""
PROCESSO: {numero_processo}
RELATOR(A): {relator}
MEDICAMENTO: {medicamento}
DECISÃO: {decisao}
"""
            )

            prompt = f"""Analise o seguinte texto de um acórdão judicial brasileiro e EXTRAIA as informações solicitadas.

TEXTO DO ACÓRDÃO:
{texto_para_analise}

IMPORTANTE: Analise o TEXTO COMPLETO acima para extrair as informações. Não confie apenas nos campos fornecidos.

Por favor, responda APENAS com um JSON válido (sem markdown, sem explicações) no seguinte formato:
{{
    "genero_relator": "M" ou "F" ou "Indeterminado",
    "confianca_genero": número de 0 a 100,
    "medicamento_extraido": "nome do medicamento encontrado no texto",
    "medicamento_valido": true ou false,
    "decisao_extraida": "texto completo da decisão (ex: CONHECER. DAR PROVIMENTO...)",
    "decisao_favoravel": true ou false,
    "observacoes": "breve explicação"
}}

REGRAS DE EXTRAÇÃO:

1. RELATOR E GÊNERO:
   - Procure por "Relator(a)" ou "Relator" no texto
   - Analise o PRIMEIRO NOME para determinar o gênero
   - Exemplos: LUCIMEIRE=F, MARIA=F, JANSEN=M, CARLOS=M, ANA=F
   - confianca_genero: 100 se claramente masculino/feminino, 50 se ambíguo

2. MEDICAMENTO:
   - Procure nomes de medicamentos no texto (geralmente em MAIÚSCULAS)
   - Medicamentos comuns: SOMATROPINA, ZOMETA, SPRAVATO, OZEMPIC, ABEMACICLIBE, etc.
   - NÃO confunda com nomes de pessoas (LUCIMEIRE, JANSEN, etc.)
   - medicamento_valido: true se for um medicamento real, false caso contrário
   - medicamento_extraido: nome exato do medicamento encontrado

3. DECISÃO:
   - Procure por "Decisão:" no texto
   - Extraia o texto completo da decisão
   - Exemplos: "CONHECER. NEGAR PROVIMENTO AO RÉU. DAR PROVIMENTO À AUTORA. UNÂNIME"
   - decisao_extraida: texto exato da decisão encontrada

4. DECISÃO FAVORÁVEL (para o paciente/autor):
   - Analise se a decisão FINAL beneficia o paciente/autor que busca o medicamento
   - Favorável (true): "DAR PROVIMENTO", "PROVIMENTO PARCIAL", "PROCEDENTE", "DEFERIR"
   - Desfavorável (false): "NEGAR PROVIMENTO", "IMPROCEDENTE", "DESPROVIDO", "INDEFERIR"
   - Se houver recursos de ambas partes: 
     * "NEGAR PROVIMENTO AO RÉU + DAR PROVIMENTO À AUTORA" = true (favorável)
     * "NEGAR PROVIMENTO À AUTORA" = false (desfavorável)
   - decisao_favoravel: true se beneficia o paciente, false se não beneficia

Responda APENAS com o JSON, nada mais."""

            response = self.model.generate_content(prompt)

            # Extrair JSON da resposta
            texto_resposta = response.text.strip()

            # Remover possíveis marcadores de código
            if texto_resposta.startswith("```"):
                linhas = texto_resposta.split("\n")
                texto_resposta = "\n".join(linhas[1:-1])

            resultado = json.loads(texto_resposta)

            logger.info(
                f"   🤖 Gemini: {relator or 'N/A'} = {resultado['genero_relator']} ({resultado['confianca_genero']}%), "
                f"Med: {resultado.get('medicamento_extraido', 'N/A')} = {'✓' if resultado.get('medicamento_valido') else '✗'}, "
                f"Decisão: {'✓ Favorável' if resultado.get('decisao_favoravel') else '✗ Desfavorável'}"
            )

            return resultado

        except json.JSONDecodeError as e:
            logger.warning(f"   ⚠️  Erro ao parsear resposta do Gemini: {e}")
            try:
                logger.debug(f"   Resposta: {response.text}")
            except Exception:
                pass
            return {
                "genero_relator": "Indeterminado",
                "confianca_genero": 0,
                "medicamento_extraido": medicamento or "",
                "medicamento_valido": None,
                "decisao_extraida": decisao or "",
                "decisao_favoravel": None,
                "observacoes": f"Erro no parse: {str(e)}",
            }
        except Exception as e:
            logger.warning(f"   ⚠️  Erro na validação Gemini: {e}")
            return {
                "genero_relator": "Indeterminado",
                "confianca_genero": 0,
                "medicamento_extraido": medicamento or "",
                "medicamento_valido": None,
                "decisao_extraida": decisao or "",
                "decisao_favoravel": None,
                "observacoes": f"Erro: {str(e)}",
            }

    def inferir_genero_lote(self, nomes: list) -> Dict[str, str]:
        """
        Infere gênero de múltiplos nomes de uma vez (mais eficiente).

        Args:
            nomes: Lista de nomes completos

        Returns:
            Dict {nome: 'M' ou 'F' ou 'Indeterminado'}
        """
        if not self.habilitado or not nomes:
            return {nome: "Indeterminado" for nome in nomes}

        try:
            nomes_unicos = list(set(nomes))

            prompt = f"""Analise os seguintes nomes de relatores/magistrados brasileiros e determine o gênero:

NOMES:
{chr(10).join(f"{i+1}. {nome}" for i, nome in enumerate(nomes_unicos))}

Responda APENAS com um JSON válido (sem markdown) no formato:
{{
    "NOME COMPLETO": "M" ou "F" ou "Indeterminado"
}}

REGRAS:
- Analise apenas o PRIMEIRO NOME (prenome) para determinar o gênero
- M = Masculino, F = Feminino, Indeterminado = nome ambíguo ou desconhecido
- Exemplos: LUCIMEIRE=F, MARIA=F, JANSEN=M, CARLOS=M, ANA=F, ROBSON=M

Responda APENAS com o JSON."""

            response = self.model.generate_content(prompt)
            texto_resposta = response.text.strip()

            if texto_resposta.startswith("```"):
                linhas = texto_resposta.split("\n")
                texto_resposta = "\n".join(linhas[1:-1])

            resultado = json.loads(texto_resposta)

            logger.info(f"   🤖 Gemini: Inferiu gênero de {len(resultado)} nomes")
            return resultado

        except Exception as e:
            logger.warning(f"   ⚠️  Erro na inferência em lote: {e}")
            return {nome: "Indeterminado" for nome in nomes}


# ==================== TESTE ====================

if __name__ == "__main__":
    # Teste básico
    logging.basicConfig(level=logging.INFO)

    print("🧪 Testando Validador Gemini\n")
    print("Para usar, configure a variável de ambiente:")
    print("export GEMINI_API_KEY='sua_chave_aqui'")
    print("\nObtenha sua chave gratuita em: https://makersuite.google.com/app/apikey\n")

    validador = ValidadorGemini()

    if validador.habilitado:
        # Teste individual
        resultado = validador.validar_processo(
            numero_processo="0711915-93.2024.8.07.0001",
            relator="LUCIMEIRE MARIA DA SILVA",
            medicamento="SOMATROPINA",
            decisao="CONHECER. NEGAR PROVIMENTO AO APELO DO RÉU. UNÂNIME",
            texto_completo="APELAÇÃO CÍVEL. PLANO DE SAÚDE. FORNECIMENTO DE MEDICAMENTO. SOMATROPINA. Relator(a): LUCIMEIRE MARIA DA SILVA. Decisão: CONHECER. NEGAR PROVIMENTO AO APELO DO RÉU. UNÂNIME",
        )

        print("📊 Resultado da validação:")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

        # Teste em lote
        print("\n🔄 Teste em lote:")
        nomes = [
            "LUCIMEIRE MARIA DA SILVA",
            "JANSEN FIALHO DE ALMEIDA",
            "ANA CANTARINO",
            "ROBSON BARBOSA DE AZEVEDO",
        ]

        generos = validador.inferir_genero_lote(nomes)
        for nome, genero in generos.items():
            print(f"   {nome}: {genero}")
    else:
        print("❌ Validador não está habilitado. Configure GEMINI_API_KEY.")
