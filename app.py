from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from io import BytesIO
import openpyxl
import requests
import msal
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuração Azure AD
CLIENT_ID = "04b07795-8ddb-461a-bbee-02f9e1bf7b46"  # Cliente público do Azure CLI
TENANT_ID = "common"
AUTHORITY_URL = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_URI = "https://localhost:8443/api/callback"
SCOPE = ["https://graph.microsoft.com/.default"]

# Armazenar tokens em memória
tokens_armazenados = {}

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
    email: str = None
    senha: str = None

@app.get("/api/login-url")
async def get_login_url():
    """Retorna URL de login do Azure AD"""
    client = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY_URL)
    
    auth_url = client.get_authorization_request_url(
        scopes=SCOPE,
        redirect_uri=REDIRECT_URI
    )
    
    print(f"[*] URL de login gerada: {auth_url[:80]}...")
    
    return {"login_url": auth_url}

@app.get("/api/callback")
async def callback(code: str = None, error: str = None):
    """Callback do Azure AD - recebe código de autorização"""
    if error:
        print(f"[ERRO] {error}")
        return RedirectResponse(url=f"/?auth=error&message={error}", status_code=302)
    
    if not code:
        raise HTTPException(status_code=400, detail="Código não fornecido")
    
    try:
        print("[*] Trocando código por token...")
        client = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY_URL)
        
        token_response = client.acquire_token_by_authorization_code(
            code=code,
            scopes=SCOPE,
            redirect_uri=REDIRECT_URI
        )
        
        if "access_token" in token_response:
            tokens_armazenados["access_token"] = token_response["access_token"]
            print("[OK] Token armazenado com sucesso")
            return RedirectResponse(url="/?auth=success", status_code=302)
        else:
            error_msg = token_response.get('error_description', 'Unknown error')
            print(f"[ERRO] {error_msg}")
            return RedirectResponse(url=f"/?auth=error&message={error_msg}", status_code=302)
            
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        return RedirectResponse(url=f"/?auth=error&message={str(e)}", status_code=302)

@app.post("/api/dados")
async def obter_dados():
    """Obtém dados do arquivo usando token OAuth2"""
    try:
        # Verificar autenticação
        if "access_token" not in tokens_armazenados:
            raise HTTPException(status_code=401, detail="Não autenticado. Faça login primeiro.")
        
        access_token = tokens_armazenados["access_token"]
        print("[*] Usando token OAuth2...")
        
        # URL da API Microsoft Graph para obter o arquivo
        arquivo_url = "https://graph.microsoft.com/v1.0/sites/governosp.sharepoint.com:/teams/SECGOVERNO-SECOM_Data:/drive/root:/001_SicomData/Miscelaneous/testeConectorPython.xlsx:/content"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/octet-stream"
        }
        
        print(f"[*] Buscando arquivo...")
        response = requests.get(
            arquivo_url,
            headers=headers,
            verify=False,
            timeout=30
        )
        
        print(f"[*] Status: {response.status_code}")
        
        if response.status_code == 401:
            del tokens_armazenados["access_token"]
            raise HTTPException(status_code=401, detail="Token expirado. Faça login novamente.")
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
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/logout")
async def logout():
    """Fazer logout"""
    if "access_token" in tokens_armazenados:
        del tokens_armazenados["access_token"]
    return {"mensagem": "Desconectado"}

# Servir arquivos estáticos
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("Iniciando servidor HTTPS com OAuth2")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8443, ssl_keyfile="key.pem", ssl_certfile="cert.pem")

