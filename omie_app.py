from fastapi import FastAPI, Request
import requests
import uvicorn

app = FastAPI()

# --- COLOQUE SUAS CHAVES DO OMIE AQUI ---
OMIE_APP_KEY = '7173616159710'
OMIE_APP_SECRET = '3359dda1c6b2883ef06c5444836958b0 '
@app.post("/webhook-entrega")
async def receber_assinatura(request: Request):
    # Recebe os dados brutos
    dados_brutos = await request.json()
    print("\n--- 🟢 Nova Assinatura Recebida! ---")
    
    # O AppSheet envia os campos dentro da chave 'Data'
    # Vamos pegar essa 'caixa' interna
    info = dados_brutos.get("Data", {})
    
    # Agora extraímos os dados de dentro de 'info'
    funcionario = info.get("Funcionario")
    # Note que o nome exato na sua planilha é Codigo_Produto_Omie
    cod_produto = info.get("Codigo_Produto_Omie") 
    qtd = info.get("Quantidade", 0)

    print(f"Processando: {funcionario} | Item: {cod_produto} | Qtd: {qtd}")

    # Chamada para o Omie
    url = "https://app.omie.com.br/api/v1/estoque/movimentos/"
    payload = {
        "call": "IncluirMovimento",
        "app_key": OMIE_APP_KEY,
        "app_secret": OMIE_APP_SECRET,
        "param": [{
            "codigo_produto_integracao": cod_produto,
            "quantidade": float(qtd),
            "tipo_movimento": "S", 
            "observacao": f"Entregue para: {funcionario}. Assinado via AppSheet."
        }]
    }

    try:
        response = requests.post(url, json=payload)
        res_json = response.json()
        print("Resposta do Omie:", res_json)
        return res_json
    except Exception as e:
        print(f"Erro ao falar com Omie: {e}")
        return {"status": "erro", "erro": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)