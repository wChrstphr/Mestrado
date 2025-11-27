import json
import csv

# carrega dados
with open("dados_completos.json", "r", encoding="utf-8") as f:
    dados = json.load(f)

# extrai decisões
resultados = []
tipos_decisao = []

for hit in dados["hits"]["hits"]:
    processo = hit["_source"]
    numero = processo["numeroProcesso"]
    classe = processo["classe"]["nome"]

    # buscando decisões nos movimentos
    decisoes_encontradas = []

    if "movimentos" in processo:
        for mov in processo["movimentos"]:
            nome_mov = mov.get("nome", "")

            # Termos expandidos para capturar mais decisões
            termos_decisao = [
                # Favoráveis
                "Procedência",
                # Desfavoráveis
                "Improcedência",
                "Improcedente",
                "Indeferido",
                "Desprovido",
                "Negado",
                "Rejeitado",
                "Não conhecido",
            ]

            if any(palavra in nome_mov for palavra in termos_decisao):
                decisoes_encontradas.append(
                    {
                        "codigo": mov.get("codigo"),
                        "nome": nome_mov,
                        "data": mov.get("dataHora"),
                    }
                )
                tipos_decisao.append(nome_mov)

    if decisoes_encontradas:
        resultados.append(
            {
                "numero_processo": numero,
                "classe": classe,
                "decisoes": decisoes_encontradas,
            }
        )

# salva resultados no dicionário json
with open("processos_com_decisoes.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False)

# salva em CSV
with open("decisoes_resumo.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["numeroProcesso", "classe", "tipo_decisao", "data_decisao"])

    for r in resultados:
        for dec in r["decisoes"]:
            writer.writerow(
                [r["numero_processo"], r["classe"], dec["nome"], dec["data"]]
            )

print(f"\nArquivos gerados:")
print(f"  - processos_com_decisoes.json (detalhado)")
print(f"  - decisoes_resumo.csv (resumido)")
