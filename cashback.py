from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from conexao import connection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://cashback-online.vercel.app"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# modelo de como as informações chegam do front
class requisicaoCompra(BaseModel):
    compra:float
    cupom: float
    vip: bool

def aplicacaoDesconto (compra, cupom, vip):
    desconto = cupom * (compra / 100)
    valorTotal = compra - desconto
    cashback = 5 * (valorTotal / 100)
    
    if valorTotal > 500:
        cashback *= 2
    
    if vip == True:
        cashback += cashback / 10
        
    return cashback


@app.post("/calcular")
async def calcular_cashback(dados: requisicaoCompra, request: Request): # o parametro dados recebe o corpo da requisição, e request da acesso aos dados brutos da requisição
    
    # Tenta pegar o IP real da nuvem; se não achar (testando local), usa o client.host
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    # X-Forwarded-For pode retornar vários IPs separados por vírgula, pega o primeiro
    ip = ip.split(",")[0].strip()
    
    cashback = aplicacaoDesconto(dados.compra, dados.cupom, dados.vip)
    
    conexao = connection() #abre conexão para para executar o select
    try:
        cursor = conexao.cursor() #abre o cursor para executar o select
        cursor.execute("""INSERT INTO consultas_cashback(ip_usuario, vip, valor_compra, cupom, cashback_calculado) values (%s, %s, %s, %s, %s)""", (ip, dados.vip, dados.compra, dados.cupom, round(cashback, 2)))
        conexao.commit() #confirma a operação no banco
    
    finally:
        cursor.close() #fecha o cursor após o uso
        conexao.close() #fecha a conexão após o uso
    
    return {
        "ip": ip,
        "compra": dados.compra,
        "cupom": dados.cupom,
        "vip": dados.vip,
        "cashback": round(cashback, 2) #arredonda o cashback para 2 casas decimais
    }
    
@app.get("/historico")
async def get_historico(request: Request): #função não preciso do corpo somente do request, só vai usar o ip de queme stá chamando
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    ip = ip.split(",")[0].strip()
    
    conexao = connection()
    try:
        cursor = conexao.cursor()
        cursor.execute("""SELECT * FROM consultas_cashback where ip_usuario = %s ORDER BY data_hora_consulta""", (ip,))
        registros = cursor.fetchall() # busca todos os resultados da query de uma vez e salvaa na variavel registros
    finally:
        cursor.close()
        conexao.close()
    
    return {
        "ip": ip,
        "historico": registros
    }
    
@app.get("/")
def health_check():
    return {"status": "ok", "mensagem": "API do Desafio rodando na nuvem!"}