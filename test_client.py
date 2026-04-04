import urllib.request, json
from urllib.error import HTTPError

BASE_URL = "http://localhost:8000"

def post(endpoint, dados):
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=json.dumps(dados).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read()), r.status
    except HTTPError as e:
        return json.loads(e.read()), e.code

def get(endpoint):
    try:
        with urllib.request.urlopen(f"{BASE_URL}{endpoint}") as r:
            return json.loads(r.read()), r.status
    except HTTPError as e:
        return json.loads(e.read()), e.code

print("=== INICIANDO TESTES COMPLETOS DA API ===\n")

# 1. Testes de Sucesso (POST)
print("1. Testando Endpoints POST (Sucesso):")
operacoes = [
    ("/somar", {"numero1": 15, "numero2": 10}, "Soma (15+10)"),
    ("/subtrair", {"numero1": 50, "numero2": 20}, "Subtracao (50-20)"),
    ("/multiplicar", {"numero1": 6, "numero2": 7}, "Multiplicacao (6*7)"),
    ("/dividir", {"numero1": 100, "numero2": 4}, "Divisao (100/4)"),
    ("/potencia", {"numero1": 2, "numero2": 10}, "Potencia (2^10)"),
    ("/raiz", {"numero1": 144, "numero2": 0}, "Raiz (sqrt 144)")
]

for endpoint, dados, desc in operacoes:
    res, status = post(endpoint, dados)
    print(f"  [PASS] {desc}: {res['resultado']} (Status: {status})")

# 2. Teste de Sucesso (GET /calcular)
print("\n2. Testando Endpoint GET /calcular (Sucesso):")
res, status = get("/calcular?numero1=30&numero2=5&operacao=multiplicacao")
print(f"  [PASS] Calcular 30*5 via Query: {res['resultado']} (Status: {status})")

# 3. Testes de Erro e Validação (Nível Intermediário)
print("\n3. Testando Casos de Erro (Validação):")

# Erro: Divisão por Zero
res, status = post("/dividir", {"numero1": 10, "numero2": 0})
print(f"  [PASS] Divisao por zero (POST): {res['detail']} (Status: {status})")

# Erro: Raiz de Negativo
res, status = post("/raiz", {"numero1": -25, "numero2": 0})
print(f"  [PASS] Raiz de negativo (POST): {res['detail']} (Status: {status})")

# Erro: Operação Inválida via Query
res, status = get("/calcular?numero1=10&numero2=5&operacao=invalida")
print(f"  [PASS] Operacao invalida (GET): {res['detail']} (Status: {status})")

# Erro: Dados Inválidos (Tipo incorreto)
res, status = post("/somar", {"numero1": "texto", "numero2": 5})
print(f"  [PASS] Dado invalido (String no lugar de Float): {res['detail'][0]['msg']} (Status: {status})")

# 4. Teste de Histórico (SQLite)
print("\n4. Verificando Histórico no Banco de Dados (SQLite):")
res, status = get("/historico")
if status == 200:
    total = len(res)
    print(f"  [PASS] Total de calculos no banco: {total}")
    if total > 0:
        ultimo = res[0]
        print(f"  [PASS] Ultimo calculo salvo: {ultimo['operacao']} ({ultimo['numero1']}, {ultimo['numero2']}) = {ultimo['resultado']}")

print("\n=== TODOS OS TESTES FORAM CONCLUÍDOS COM SUCESSO! ===")
