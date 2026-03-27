from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from io import BytesIO
import openpyxl
import requests
import msal
import urllib3
import json
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuração Azure AD para autenticação não-interativa
CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"
AUTHORITY = "https://login.microsoftonline.com/organizations"  # Mudado de /common para /organizations
SCOPE = ["https://graph.microsoft.com/.default"]

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CredentialsRequest(BaseModel):
    email: str
    senha: str

def obter_token(email: str, senha: str):
    """Obtém token de acesso usando credenciais do usuário"""
    try:
        app_client = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)
        
        # Tentar autenticação não-interativa com usuário/senha
        token_response = app_client.acquire_token_by_username_password(
            username=email,
            password=senha,
            scopes=SCOPE
        )
        
        if "access_token" in token_response:
            return token_response["access_token"]
        else:
            error = token_response.get("error", "Unknown error")
            error_desc = token_response.get("error_description", "")
            raise Exception(f"{error}: {error_desc}")
            
    except Exception as e:
        print(f"[ERRO] Erro ao obter token: {str(e)}")
        raise

@app.post("/api/dados")
async def obter_dados(request: CredentialsRequest):
    """Obtém dados do arquivo usando credenciais"""
    try:
        email = request.email.strip()
        senha = request.senha.strip()
        
        if not email or not senha:
            raise HTTPException(status_code=400, detail="Email e senha são obrigatórios")
        
        print(f"[*] Autenticando como: {email}")
        
        # Obter token
        print("[*] Obtendo token de acesso...")
        access_token = obter_token(email, senha)
        print("[OK] Token obtido com sucesso")
        
        # Usar token para acessar arquivo
        print("[*] Buscando arquivo no OneDrive...")
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/octet-stream"
        }
        
        # URL do arquivo no Microsoft Graph (OneDrive pessoal)
        # Caminho: myfiles/teste/testeConectorPython.xlsx
        arquivo_url = "https://graph.microsoft.com/v1.0/me/drive/root:/teste/testeConectorPython.xlsx:/content"
        
        response = requests.get(
            arquivo_url,
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
            print(f"[ERRO] {response.status_code}: {response.text[:200]}")
            raise Exception(f"Erro {response.status_code}")
        
        print("[OK] Arquivo baixado")
        
        # Processar Excel
        excel_stream = BytesIO(response.content)
        workbook = openpyxl.load_workbook(excel_stream)
        worksheet = workbook.active
        
        headers_list = []
        dados = []
        
        for idx, row in enumerate(worksheet.iter_rows(values_only=True)):
            if row and any(cell is not None for cell in row):
                if idx == 0:
                    headers_list = [str(cell) if cell else "" for cell in row]
                else:
                    row_data = [str(cell) if cell is not None else "" for cell in row]
                    dados.append(row_data)
        
        print(f"[OK] {len(dados)} linhas extraídas")
        
        return {
            "sucesso": True,
            "headers": headers_list,
            "dados": dados,
            "total_linhas": len(dados)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERRO] {type(e).__name__}: {str(e)}")
        
        if "Conditional Access" in str(e) or "AADSTS" in str(e):
            raise HTTPException(status_code=403, detail="Acesso bloqueado por política de acesso condicional. Contacte administrador.")
        
        raise HTTPException(status_code=500, detail=str(e))

# Servir arquivos estáticos (deve estar APÓS as rotas da API)
static_dir = os.path.dirname(os.path.abspath(__file__))
app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("Iniciando servidor HTTPS com autenticação JSON")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8443, ssl_keyfile="key.pem", ssl_certfile="cert.pem")

