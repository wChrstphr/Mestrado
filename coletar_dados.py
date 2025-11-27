import requests
import json
import csv

url = "https://api-publica.datajud.cnj.jus.br/api_publica_tjce/_search"  # url do TJSP
api_key = "APIKey cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=="  # Chave pública

payload = json.dumps(
    {
        "size": 10000,
        "query": {"match": {"assuntos.codigo": "9859"}},
        "sort": [{"dataAjuizamento": {"order": "desc"}}],  # ou asc
    }
)

headers = {"Authorization": api_key, "Content-Type": "application/json"}

response = requests.request(
    "POST", url, headers=headers, data=payload
)  
dados_dict = response.json()  


# salvando em Json
with open("dados_completos.json", "w", encoding="utf-8") as f:
    json.dump(dados_dict, f, indent=2, ensure_ascii=False)
print("Dados completos salvos em 'dados_completos.json'")

# salvando em csv
processos = dados_dict["hits"]["hits"]

numeros = []
for processo in processos:
    numero_processo = processo["_source"]["numeroProcesso"]
    numeros.append(numero_processo)

with open("numeros_processos.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["numeroProcesso"])
    for num in numeros:
        writer.writerow([num])
