from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from io import BytesIO
import openpyxl
import requests
import base64
import urllib3
import traceback

# Desabilitar avisos de SSL inseguro
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Constantes do SharePoint
SITE_URL = "https://governosp.sharepoint.com/teams/SECGOVERNO-SECOM_Data"
# URL da API REST para o arquivo (com encoding correto)
ARQUIVO_URL = "https://governosp.sharepoint.com/teams/SECGOVERNO-SECOM_Data/_api/web/GetFileByServerRelativeUrl('%2Fteams%2FSECGOVERNO-SECOM_Data%2FShared%20Documents%2F001_SicomData%2FMiscelaneous%2FtesteConectorPython.xlsx')/$value"

app = FastAPI()

# CORS para aceitar requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CredenciaisRequest(BaseModel):
    email: str
    senha: str

@app.post("/api/dados")
async def obter_dados(request: CredenciaisRequest):
    try:
        email = request.email.strip()
        senha = request.senha.strip()
        
        if not email or not senha:
            raise HTTPException(status_code=400, detail="Email e senha são obrigatórios")
        
        print(f"[*] Autenticando como: {email}")
        
        # Criar autenticação Basic (base64 encoded)
        credentials = f"{email}:{senha}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            'Authorization': f'Basic {encoded_credentials}'
        }
        
        # Fazer requisição para baixar arquivo
        print(f"[*] URL: {ARQUIVO_URL}")
        print("[*] Buscando arquivo...")
        
        response = requests.get(
            ARQUIVO_URL, 
            headers=headers,
            verify=False,
            timeout=30
        )
        
        print(f"[*] Status: {response.status_code}")
        
        if response.status_code == 401:
            raise HTTPException(status_code=401, detail="Credenciais inválidas ou acesso negado.")
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
        elif response.status_code != 200:
            print(f"[ERRO] Status {response.status_code}")
            print(f"[ERRO] Resposta: {response.text[:500]}")
            raise Exception(f"Erro na requisição: {response.status_code}")
        
        print("[OK] Arquivo baixado")
        
        # Processar Excel
        excel_stream = BytesIO(response.content)
        workbook = openpyxl.load_workbook(excel_stream)
        worksheet = workbook.active
        
        # Extrair dados (primeira linha é cabeçalho)
        headers = []
        dados = []
        
        for idx, row in enumerate(worksheet.iter_rows(values_only=True)):
            if row and any(cell is not None for cell in row):
                if idx == 0:
                    headers = [str(cell) if cell else "" for cell in row]
                else:
                    row_data = [str(cell) if cell is not None else "" for cell in row]
                    dados.append(row_data)
        
        print(f"[OK] Dados extraídos: {len(dados)} linhas, {len(headers)} colunas")
        
        return {
            "sucesso": True,
            "headers": headers,
            "dados": dados,
            "total_linhas": len(dados)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERRO] Exceção: {type(e).__name__}")
        print(f"[ERRO] Mensagem: {str(e)}")
        print(f"[ERRO] Traceback:\n{traceback.format_exc()}")
        
        erro_msg = str(e).lower()
        
        if "401" in str(e) or "unauthorized" in erro_msg:
            raise HTTPException(status_code=401, detail="Credenciais inválidas ou acesso negado.")
        elif "404" in str(e) or "not found" in erro_msg:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado.")
        else:
            raise HTTPException(status_code=500, detail=f"Erro: {str(e)}")

# Servir arquivos estáticos (CSS, JS, etc) - DEVE SER O ÚLTIMO
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("Iniciando servidor HTTPS")
    print("Acesse: https://localhost:8443")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8443, ssl_keyfile="key.pem", ssl_certfile="cert.pem")

