import json
from collections import Counter
from datetime import datetime

# Carregar dados
with open("dados_completos.json", "r", encoding="utf-8") as f:
    data = json.load(f)

processos = data["hits"]["hits"]
print(f"Total de processos: {len(processos)}")
print("\n" + "=" * 80)

# Analisar estrutura detalhada
processo_exemplo = processos[0]["_source"]

print("\n1. MOVIMENTOS:")
movimentos = processo_exemplo.get("movimentos", [])
print(f"   Total de movimentos: {len(movimentos)}")
if movimentos:
    print(f"   Exemplo de movimento:")
    print(f"   {json.dumps(movimentos[0], indent=4, ensure_ascii=False)}")

print("\n2. ÓRGÃO JULGADOR:")
print(
    json.dumps(processo_exemplo.get("orgaoJulgador", {}), indent=4, ensure_ascii=False)
)

print("\n3. CLASSE:")
print(json.dumps(processo_exemplo.get("classe", {}), indent=4, ensure_ascii=False))

print("\n4. ASSUNTOS:")
assuntos = processo_exemplo.get("assuntos", [])
print(f"   Total: {len(assuntos)}")
for assunto in assuntos[:3]:
    print(f"   - {assunto}")

print("\n5. FORMATO:")
print(f"   {processo_exemplo.get('formato', {})}")

print("\n6. GRAU:")
print(f"   {processo_exemplo.get('grau')}")

print("\n7. DATAS:")
print(f"   Ajuizamento: {processo_exemplo.get('dataAjuizamento')}")
print(f"   Última atualização: {processo_exemplo.get('dataHoraUltimaAtualizacao')}")

print("\n8. SISTEMA:")
print(f"   {processo_exemplo.get('sistema')}")

print("\n9. TRIBUNAL:")
print(f"   {processo_exemplo.get('tribunal')}")

print("\n10. NÍVEL SIGILO:")
print(f"   {processo_exemplo.get('nivelSigilo')}")

# Estatísticas agregadas
print("\n" + "=" * 80)
print("\nESTATÍSTICAS AGREGADAS:")

print("\n- Distribuição de GRAUS:")
graus = [p["_source"].get("grau", "N/A") for p in processos]
for grau, count in Counter(graus).most_common():
    print(f"  {grau}: {count}")

print("\n- Distribuição de CLASSES (top 10):")
classes = [p["_source"].get("classe", {}).get("nome", "N/A") for p in processos]
for classe, count in Counter(classes).most_common(10):
    print(f"  {classe}: {count}")

print("\n- Distribuição de FORMATOS:")
formatos = [p["_source"].get("formato", {}).get("nome", "N/A") for p in processos]
for formato, count in Counter(formatos).most_common():
    print(f"  {formato}: {count}")

print("\n- Quantidade de ASSUNTOS por processo:")
qtd_assuntos = [len(p["_source"].get("assuntos", [])) for p in processos]
print(f"  Média: {sum(qtd_assuntos)/len(qtd_assuntos):.2f}")
print(f"  Mínimo: {min(qtd_assuntos)}")
print(f"  Máximo: {max(qtd_assuntos)}")

print("\n- Quantidade de MOVIMENTOS por processo:")
qtd_movimentos = [len(p["_source"].get("movimentos", [])) for p in processos]
print(f"  Média: {sum(qtd_movimentos)/len(qtd_movimentos):.2f}")
print(f"  Mínimo: {min(qtd_movimentos)}")
print(f"  Máximo: {max(qtd_movimentos)}")

print("\n- Top 10 ASSUNTOS mais frequentes:")
todos_assuntos = []
for p in processos:
    for assunto in p["_source"].get("assuntos", []):
        todos_assuntos.append(assunto.get("nome", "N/A"))
for assunto, count in Counter(todos_assuntos).most_common(10):
    print(f"  {assunto}: {count}")

print("\n- Distribuição de MUNICÍPIOS (top 10):")
municipios = []
for p in processos:
    org = p["_source"].get("orgaoJulgador", {})
    if isinstance(org, dict):
        mun = (
            org.get("nomeOrgao", "N/A")
            if "nomeOrgao" in org
            else org.get("nome", "N/A")
        )
        municipios.append(mun)
for mun, count in Counter(municipios).most_common(10):
    print(f"  {mun}: {count}")
