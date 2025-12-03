"""
Script para gerar features do dados_completos.json e integrá-las com dados_processos_com_sexo.csv
Gera dataset completo com 26 features para modelo de Machine Learning
"""

import json
import pandas as pd
from datetime import datetime
import re
from collections import Counter


def extrair_tipo_vara(nome_orgao):
    """Extrai o tipo de vara do nome do órgão julgador"""
    nome_lower = nome_orgao.lower()

    if "infancia" in nome_lower or "juventude" in nome_lower:
        return "Infância_Juventude"
    elif "fazenda" in nome_lower:
        return "Fazenda_Publica"
    elif "juizado especial" in nome_lower:
        return "Juizado_Especial"
    elif "turma recursal" in nome_lower:
        return "Turma_Recursal"
    elif "vice-presidencia" in nome_lower or "presidencia" in nome_lower:
        return "Presidencia"
    else:
        return "Outros"


def extrair_features_temporais(data_ajuizamento_str, data_atualizacao_str):
    """Extrai features temporais das datas"""
    try:
        # Converter dataAjuizamento (formato: 20250930000000)
        data_ajuiz = datetime.strptime(data_ajuizamento_str, "%Y%m%d%H%M%S")

        # Converter dataHoraUltimaAtualizacao (formato ISO) - remover timezone para evitar erro
        data_atual_str = data_atualizacao_str.replace("Z", "").split(".")[0]
        data_atual = datetime.fromisoformat(data_atual_str)

        # Calcular diferença
        dias_desde_ajuizamento = (data_atual - data_ajuiz).days

        return {
            "dias_desde_ajuizamento": dias_desde_ajuizamento,
            "ano_ajuizamento": data_ajuiz.year,
            "mes_ajuizamento": data_ajuiz.month,
            "trimestre_ajuizamento": (data_ajuiz.month - 1) // 3 + 1,
            "dia_semana_ajuizamento": data_ajuiz.weekday(),
        }
    except Exception as e:
        print(f"Erro ao processar datas: {e}")
        return {
            "dias_desde_ajuizamento": 0,
            "ano_ajuizamento": 0,
            "mes_ajuizamento": 0,
            "trimestre_ajuizamento": 0,
            "dia_semana_ajuizamento": 0,
        }


def classificar_classe(classe_nome):
    """Classifica a classe processual em categorias principais"""
    classes_principais = [
        "Procedimento Comum Cível",
        "Agravo de Instrumento",
        "Apelação Cível",
        "Procedimento do Juizado Especial da Fazenda Pública",
        "Cumprimento de sentença",
        "Procedimento do Juizado Especial Cível",
        "Cumprimento de Sentença contra a Fazenda Pública",
        "Ação Civil Pública",
        "Recurso Inominado Cível",
        "Cumprimento Provisório de Sentença",
    ]

    if classe_nome in classes_principais:
        return classe_nome
    else:
        return "Outros"


def extrair_features_assuntos(assuntos):
    """Extrai features relacionadas aos assuntos do processo"""
    assuntos_text = " ".join([a.get("nome", "").lower() for a in assuntos])

    return {
        "qtd_assuntos": len(assuntos),
        "tem_medicamento": 1 if "medicamento" in assuntos_text else 0,
        "tem_tutela_urgencia": (
            1
            if ("tutela" in assuntos_text and "urgencia" in assuntos_text)
            or "liminar" in assuntos_text
            else 0
        ),
        "tem_obrigacao_fazer": 1 if "obrigação de fazer" in assuntos_text else 0,
        "tem_dano_moral": 1 if "dano moral" in assuntos_text else 0,
        "area_saude": (
            1
            if any(
                palavra in assuntos_text
                for palavra in [
                    "medicamento",
                    "tratamento",
                    "oncológico",
                    "saúde",
                    "hospitalar",
                ]
            )
            else 0
        ),
        "assunto_principal": (
            assuntos[0].get("nome", "Desconhecido") if assuntos else "Desconhecido"
        ),
    }


def extrair_features_movimentos(movimentos, dias_desde_ajuizamento):
    """Extrai features relacionadas aos movimentos do processo"""
    qtd_movimentos = len(movimentos)

    # Calcular velocidade (evitar divisão por zero)
    velocidade = (
        qtd_movimentos / dias_desde_ajuizamento if dias_desde_ajuizamento > 0 else 0
    )

    # Verificar movimentos recentes (últimos 30 dias)
    try:
        data_limite = datetime.now() - pd.Timedelta(days=30)
        movimentos_recentes = 0

        for mov in movimentos:
            data_mov_str = mov.get("dataHora", "")
            if data_mov_str:
                data_mov = datetime.fromisoformat(data_mov_str.replace("Z", "+00:00"))
                if data_mov >= data_limite:
                    movimentos_recentes += 1
    except:
        movimentos_recentes = 0

    # Extrair tipo de distribuição do primeiro movimento
    tipo_distribuicao = "Desconhecido"
    if movimentos:
        primeiro_mov = movimentos[0]
        complementos = primeiro_mov.get("complementosTabelados", [])
        for comp in complementos:
            if "distribuicao" in comp.get("descricao", "").lower():
                tipo_distribuicao = comp.get("nome", "Desconhecido")
                break

    return {
        "qtd_movimentos": qtd_movimentos,
        "velocidade_movimentos": round(velocidade, 4),
        "movimentos_recentes": movimentos_recentes,
        "tipo_distribuicao": tipo_distribuicao,
    }


def processar_processo(processo_source):
    """Processa um processo e extrai todas as features"""

    # Dados básicos
    numero_processo = processo_source.get("numeroProcesso", "")

    # Features temporais
    features_temporais = extrair_features_temporais(
        processo_source.get("dataAjuizamento", ""),
        processo_source.get("dataHoraUltimaAtualizacao", ""),
    )

    # Features categóricas
    grau = processo_source.get("grau", "Desconhecido")
    classe_info = processo_source.get("classe", {})
    classe_nome = classe_info.get("nome", "Desconhecido")
    classe_categoria = classificar_classe(classe_nome)

    # Órgão julgador
    orgao_julgador = processo_source.get("orgaoJulgador", {})
    nome_orgao = orgao_julgador.get("nome", "")
    tipo_vara = extrair_tipo_vara(nome_orgao)
    municipio_fortaleza = 1 if "FORTALEZA" in nome_orgao.upper() else 0

    # Sistema e formato
    sistema = processo_source.get("sistema", {}).get("nome", "Desconhecido")
    formato = processo_source.get("formato", {}).get("nome", "Desconhecido")

    # Features de assuntos
    assuntos = processo_source.get("assuntos", [])
    features_assuntos = extrair_features_assuntos(assuntos)

    # Features de movimentos
    movimentos = processo_source.get("movimentos", [])
    features_movimentos = extrair_features_movimentos(
        movimentos, features_temporais["dias_desde_ajuizamento"]
    )

    # Complexidade
    complexidade_score = (
        features_assuntos["qtd_assuntos"] * features_movimentos["qtd_movimentos"]
    )

    # Verificar se tem recurso
    tem_recurso = (
        1
        if any(
            palavra in classe_nome.lower()
            for palavra in ["agravo", "apelação", "recurso"]
        )
        else 0
    )

    # Montar dicionário com todas as features
    features = {
        "numero_processo": numero_processo,
        **features_temporais,
        "grau": grau,
        "classe_categoria": classe_categoria,
        "tipo_vara": tipo_vara,
        "municipio_fortaleza": municipio_fortaleza,
        "sistema": sistema,
        "formato": formato,
        **features_assuntos,
        **features_movimentos,
        "complexidade_score": complexidade_score,
        "tem_recurso": tem_recurso,
    }

    return features


def executar_geracao_features():
    """
    Função principal: gera features para modelo ML
    """
    print("=" * 80)
    print("GERAÇÃO DE FEATURES PARA MODELO ML")
    print("=" * 80)

    # 1. Carregar dados_completos.json
    print("\n[1/4] Carregando dados_completos.json...")
    with open("data/dados_completos.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    processos = data["hits"]["hits"]
    print(f"   ✓ {len(processos)} processos carregados")

    # 2. Extrair features de cada processo
    print("\n[2/4] Extraindo features...")
    features_list = []

    for i, processo in enumerate(processos):
        if (i + 1) % 1000 == 0:
            print(f"   Processando: {i+1}/{len(processos)}")

        processo_source = processo["_source"]
        features = processar_processo(processo_source)
        features_list.append(features)

    df_features = pd.DataFrame(features_list)
    print(f"   ✓ {len(df_features)} processos com features extraídas")
    print(f"   ✓ {len(df_features.columns)} colunas geradas")

    # 3. Carregar dados_processos_com_sexo.csv e fazer merge
    print("\n[3/4] Integrando com dados_processos_com_sexo.csv...")
    try:
        df_sexo = pd.read_csv("data/dados_processos_com_sexo.csv")
        print(f"   ✓ {len(df_sexo)} processos com dados de sexo carregados")

        # Converter numero_processo para string com zeros à esquerda (20 dígitos)
        df_sexo["numero_processo"] = (
            df_sexo["numero_processo"].astype(str).str.zfill(20)
        )
        df_features["numero_processo"] = df_features["numero_processo"].astype(str)

        # Fazer merge pelo numero_processo
        df_final = df_features.merge(
            df_sexo[
                [
                    "numero_processo",
                    "sexo_juiz",
                    "sexo_requerente",
                    "sentenca_favoravel",
                    "status",
                ]
            ],
            on="numero_processo",
            how="inner",
        )

        print(f"   ✓ Merge realizado: {len(df_final)} processos no dataset final")

    except FileNotFoundError:
        print("   ⚠ Arquivo dados_processos_com_sexo.csv não encontrado")
        print("   → Continuando apenas com features extraídas...")
        df_final = df_features

    # 4. Salvar dataset final
    print("\n[4/4] Salvando dataset_ml_completo.csv...")
    output_file = "data/dataset_ml_completo.csv"
    df_final.to_csv(output_file, index=False, encoding="utf-8")
    print(f"   ✓ Dataset salvo: {output_file}")

    # Estatísticas finais
    print("\n" + "=" * 80)
    print("RESUMO DO DATASET FINAL")
    print("=" * 80)
    print(f"\nTotal de processos: {len(df_final)}")
    print(f"Total de features: {len(df_final.columns)}")
    print(f"\nColunas do dataset:")
    for i, col in enumerate(df_final.columns, 1):
        print(f"  {i:2d}. {col}")

    # Estatísticas descritivas
    print(f"\n\nTipos de dados:")
    print(df_final.dtypes)

    print(f"\n\nPrimeiras linhas do dataset:")
    print(df_final.head())

    print(f"\n\nEstatísticas numéricas:")
    print(df_final.describe())

    # Verificar valores faltantes
    print(f"\n\nValores faltantes:")
    missing = df_final.isnull().sum()
    if missing.sum() > 0:
        print(missing[missing > 0])
    else:
        print("   ✓ Nenhum valor faltante!")

    print("\n" + "=" * 80)
    print("✓ PROCESSO CONCLUÍDO!")
    print("=" * 80)


if __name__ == "__main__":
    executar_geracao_features()
