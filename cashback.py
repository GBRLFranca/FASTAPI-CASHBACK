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
        
    cashbackInteiro = int(cashback)
    
    return cashbackInteiro


@app.post("/calcular")
async def calcular_cashback(dados: requisicaoCompra, request: Request):
    
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    ip = ip.split(",")[0].strip()
    
    cashback = aplicacaoDesconto(dados.compra, dados.cupom, dados.vip)
    
    conexao = connection() 
    try:
        cursor = conexao.cursor() 
        cursor.execute("""INSERT INTO consultas_cashback(ip_usuario, vip, valor_compra, cupom, cashback_calculado) values (%s, %s, %s, %s, %s)""", (ip, dados.vip, dados.compra, dados.cupom, round(cashback, 2)))
        conexao.commit() 
    
    finally:
        cursor.close() 
        conexao.close() 
    
    return {
        "ip": ip,
        "compra": dados.compra,
        "cupom": dados.cupom,
        "vip": dados.vip,
        "cashback": cashback
    }
    
@app.get("/historico")
async def get_historico(request: Request): 
    ip = request.headers.get("X-Forwarded-For", request.client.host)
    ip = ip.split(",")[0].strip()
    
    conexao = connection()
    try:
        cursor = conexao.cursor()
        cursor.execute("""SELECT * FROM consultas_cashback where ip_usuario = %s ORDER BY data_hora_consulta""", (ip,))
        registros = cursor.fetchall() 
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