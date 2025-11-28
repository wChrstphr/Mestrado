"""
Módulo para Inferência de Sexo
Enriquece dados de processos com informação de sexo baseado em base de nomes brasileiros

ROADMAP DE FUNÇÕES:
==================

1. CARREGAMENTO DE DADOS
   └── carregar_banco_nomes()        : Carrega base de nomes (.csv.gz)
                                        - Detecta encoding e colunas
                                        - Retorna DataFrame com nomes e classificações

2. EXTRAÇÃO E NORMALIZAÇÃO
   └── extrair_primeiro_nome()       : Extrai e normaliza primeiro nome
                                        - Remove espaços extras
                                        - Converte para maiúsculas
                                        - Trata valores nulos

3. BUSCA E MATCHING
   └── buscar_sexo()                 : Busca sexo no banco de nomes
                                        - Matching case-insensitive
                                        - Resolve múltiplas entradas (mode)
                                        - Retorna: 'M', 'F' ou 'Indefinido'

4. PROCESSAMENTO EM LOTE
   └── inferir_sexo_processos()      : Aplica inferência em todos os processos
                                        - Cria colunas temporárias de primeiro nome
                                        - Aplica busca com pandas.apply()
                                        - Remove colunas temporárias
                                        - Retorna DataFrame enriquecido

5. ORQUESTRAÇÃO
   └── main()                        : Função principal
                                        - Valida existência de arquivos
                                        - Configura colunas do banco de nomes
                                        - Executa inferência
                                        - Salva resultado final
                                        - Exibe estatísticas e amostras
"""

import pandas as pd
import os

# Configurações
ARQUIVO_PROCESSOS = "dados_processos_tjce.csv"
ARQUIVO_NOMES = "nomes.csv.gz"
ARQUIVO_SAIDA = "dados_processos_com_sexo.csv"


def carregar_banco_nomes(arquivo_nomes):
    """
    Carrega o banco de dados de nomes brasileiros.
    Ajuste as colunas conforme a estrutura do seu arquivo.
    """
    df_nomes = pd.read_csv(
        arquivo_nomes,
        compression="gzip",
        encoding="utf-8",
    )

    return df_nomes


def extrair_primeiro_nome(nome_completo):
    """
    Extrai o primeiro nome de um nome completo.
    """
    if pd.isna(nome_completo) or nome_completo == "":
        return None

    # Remove espaços extras e pega o primeiro nome
    primeiro_nome = str(nome_completo).strip().split()[0]
    return primeiro_nome.upper()  # Normaliza para maiúsculas


def buscar_sexo(primeiro_nome, df_nomes, coluna_nome="nome", coluna_sexo="sexo"):
    """
    Busca o sexo no banco de dados de nomes.

    Args:
        primeiro_nome: Primeiro nome a buscar
        df_nomes: DataFrame com banco de nomes
        coluna_nome: Nome da coluna que contém os nomes
        coluna_sexo: Nome da coluna que contém o sexo

    Returns:
        'M', 'F' ou 'Indefinido'
    """
    if primeiro_nome is None:
        return "Indefinido"

    # Busca o nome no banco
    resultado = df_nomes[df_nomes[coluna_nome].str.upper() == primeiro_nome]

    if len(resultado) == 0:
        return "Indefinido"
    elif len(resultado) == 1:
        return resultado.iloc[0][coluna_sexo]


def inferir_sexo_processos(
    arquivo_processos, df_nomes, coluna_nome="nome", coluna_sexo="sexo"
):
    """
    Infere o sexo do juiz e requerente nos processos.
    """
    df_processos = pd.read_csv(arquivo_processos, encoding="utf-8")
    # Extrai primeiro nome e infere sexo
    df_processos["primeiro_nome_juiz"] = df_processos["juiz"].apply(
        extrair_primeiro_nome
    )
    df_processos["primeiro_nome_requerente"] = df_processos["requerente"].apply(
        extrair_primeiro_nome
    )
    # print primeiros registros de df_processos
    print("\nPrimeiros registros de df_processos após extração de primeiros nomes:")
    print(df_processos.head())

    df_processos["sexo_juiz"] = df_processos["primeiro_nome_juiz"].apply(
        lambda x: buscar_sexo(x, df_nomes, coluna_nome, coluna_sexo)
    )

    df_processos["sexo_requerente"] = df_processos["primeiro_nome_requerente"].apply(
        lambda x: buscar_sexo(x, df_nomes, coluna_nome, coluna_sexo)
    )

    # Remove colunas temporárias de primeiro nome
    df_processos = df_processos.drop(
        columns=["primeiro_nome_juiz", "primeiro_nome_requerente"]
    )

    return df_processos


def main():
    """
    Função principal.
    """
    # Verifica se os arquivos existem
    if not os.path.exists(ARQUIVO_PROCESSOS):
        print(f"Erro: Arquivo {ARQUIVO_PROCESSOS} não encontrado!")
        return

    if not os.path.exists(ARQUIVO_NOMES):
        print(f"Erro: Arquivo {ARQUIVO_NOMES} não encontrado!")
        print(f"Por favor, adicione o banco de dados de nomes brasileiros ao projeto.")
        return

    # Carrega banco de nomes
    df_nomes = carregar_banco_nomes(ARQUIVO_NOMES)

    # IMPORTANTE: Ajuste os nomes das colunas conforme seu arquivo
    # Exemplos comuns: 'nome', 'first_name', 'name'
    # Exemplos comuns: 'sexo', 'gender', 'sex'
    coluna_nome = "first_name"  # AJUSTE AQUI
    coluna_sexo = "classification"  # AJUSTE AQUI

    if coluna_nome not in df_nomes.columns:
        print(f"\nERRO: Coluna '{coluna_nome}' não encontrada!")
        print(f"Colunas disponíveis: {df_nomes.columns.tolist()}")
        print(f"Ajuste a variável 'coluna_nome' no código.")
        return

    if coluna_sexo not in df_nomes.columns:
        print(f"\nERRO: Coluna '{coluna_sexo}' não encontrada!")
        print(f"Colunas disponíveis: {df_nomes.columns.tolist()}")
        print(f"Ajuste a variável 'coluna_sexo' no código.")
        return

    # Infere sexo nos processos
    df_resultado = inferir_sexo_processos(
        ARQUIVO_PROCESSOS, df_nomes, coluna_nome, coluna_sexo
    )

    # Salva resultado
    df_resultado.to_csv(ARQUIVO_SAIDA, index=False, encoding="utf-8")
    print(f"\n✓ Resultado salvo em {ARQUIVO_SAIDA}")

    # Estatísticas
    print(f"\n{'='*60}")
    print(f"ESTATÍSTICAS")
    print(f"{'='*60}")

    print(f"\nSexo dos Juízes:")
    print(df_resultado["sexo_juiz"].value_counts())

    print(f"\nSexo dos Requerentes:")
    print(df_resultado["sexo_requerente"].value_counts())

    # Amostra do resultado
    print(f"\n{'='*60}")
    print(f"AMOSTRA DO RESULTADO")
    print(f"{'='*60}")
    print(df_resultado[["juiz", "sexo_juiz", "requerente", "sexo_requerente"]].head(10))


if __name__ == "__main__":
    main()
