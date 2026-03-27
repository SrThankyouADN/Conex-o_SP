from fastapi import FastAPI, HTTPException, Header
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
import uuid
from typing import Optional

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

# Armazenamento de sessões em memória
# token -> {"email": "user@domain.com", "password": "pass"}
sessions = {}

class CredentialsRequest(BaseModel):
    email: str
    senha: str
    caminho_arquivo: str = "teste/testeConectorPython.xlsx"  # Caminho padrão, pode ser alterado

class TokenRequest(BaseModel):
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

def extrair_credenciais_token(authorization_header: Optional[str] = None):
    """Extrai email e senha do token no header Authorization"""
    if not authorization_header:
        raise HTTPException(status_code=401, detail="Autorização necessária")
    
    # Esperado: "Bearer <token>"
    parts = authorization_header.split(" ")
    if len(parts) != 2 or parts[0] != "Bearer":
        raise HTTPException(status_code=401, detail="Formato de autorização inválido")
    
    token = parts[1]
    
    if token not in sessions:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    creds = sessions[token]
    return creds["email"], creds["senha"]

# ============= ENDPOINTS =============

@app.post("/api/token")
async def criar_token(request: TokenRequest):
    """Cria um token de sessão usando email e senha"""
    try:
        email = request.email.strip()
        senha = request.senha.strip()
        
        if not email or not senha:
            raise HTTPException(status_code=400, detail="Email e senha são obrigatórios")
        
        print(f"[*] Autenticando: {email}")
        
        # Validar credenciais tentando obter um token MSAL
        access_token = obter_token(email, senha)
        
        print("[OK] Credenciais validadas")
        
        # Gerar token de sessão único
        session_token = str(uuid.uuid4())
        sessions[session_token] = {
            "email": email,
            "senha": senha
        }
        
        return {
            "sucesso": True,
            "token": session_token
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        raise HTTPException(status_code=401, detail=f"Erro de autenticação: {str(e)}")

@app.get("/api/sites")
async def listar_sites(authorization: Optional[str] = Header(None)):
    """Lista todos os sites/grupos disponíveis"""
    try:
        email, senha = extrair_credenciais_token(authorization)
        print(f"[*] Listando sites para: {email}")
        
        # Obter token
        access_token = obter_token(email, senha)
        
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        
        # Listar grupos que o usuário é membro
        response = requests.get(
            "https://graph.microsoft.com/v1.0/me/memberOf",
            headers=headers,
            verify=False,
            timeout=30
        )
        
        if response.status_code == 200:
            items = response.json().get("value", [])
            
            # Filtrar apenas grupos e teams
            sites = []
            for item in items:
                # Filtrar por @odata.type para pegar apenas grupos
                odata_type = item.get("@odata.type", "")
                if "group" in odata_type.lower():
                    sites.append({
                        "id": item.get("id"),
                        "nome": item.get("displayName", "Unknown"),
                        "mail": item.get("mail", ""),
                        "tipo": "grupo"
                    })
            
            print(f"[OK] {len(sites)} sites encontrados")
            
            return sites
        else:
            print(f"[ERRO] {response.status_code}: {response.text[:200]}")
            raise HTTPException(status_code=response.status_code, detail="Erro ao listar sites")
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sites/{site_id}/arquivos")
async def listar_arquivos_site(site_id: str, authorization: Optional[str] = Header(None)):
    """Lista arquivos de um site específico (raiz)"""
    try:
        email, senha = extrair_credenciais_token(authorization)
        print(f"[*] Listando arquivos do site: {site_id}")
        
        # Obter token
        access_token = obter_token(email, senha)
        
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        
        # Obter o drive do grupo
        drive_url = f"https://graph.microsoft.com/v1.0/groups/{site_id}/drive"
        drive_resp = requests.get(drive_url, headers=headers, verify=False, timeout=30)
        
        if drive_resp.status_code != 200:
            raise HTTPException(status_code=404, detail="Drive não encontrado neste site")
        
        drive_id = drive_resp.json().get("id")
        print(f"    Drive ID: {drive_id}")
        
        # Listar arquivos da raiz
        item_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root/children"
        
        pastas = []
        arquivos = []
        
        # Suportar paginação
        while item_url:
            items_resp = requests.get(item_url, headers=headers, verify=False, timeout=30)
            
            if items_resp.status_code != 200:
                print(f"[ERRO] {items_resp.status_code}: {items_resp.text[:200]}")
                raise HTTPException(status_code=404, detail="Caminho não encontrado ou não tem permissão")
            
            data = items_resp.json()
            items = data.get("value", [])
            
            for item in items:
                if item.get("folder"):
                    pastas.append({
                        "id": item.get("id"),
                        "nome": item.get("name"),
                        "tipo": "pasta"
                    })
                else:
                    arquivos.append({
                        "id": item.get("id"),
                        "nome": item.get("name"),
                        "size": item.get("size", 0),
                        "drive_id": drive_id
                    })
            
            # Verificar se há mais páginas
            item_url = data.get("@odata.nextLink")
        
        print(f"[OK] {len(pastas)} pastas, {len(arquivos)} arquivos")
        
        return {
            "drive_id": drive_id,
            "pastas": pastas,
            "arquivos": arquivos
        }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/pastas/{drive_id}/{folder_id}/conteudo")
async def listar_conteudo_pasta(drive_id: str, folder_id: str, authorization: Optional[str] = Header(None)):
    """Lista o conteúdo de uma pasta específica"""
    try:
        email, senha = extrair_credenciais_token(authorization)
        print(f"[*] Listando conteúdo da pasta: drive={drive_id}, folder={folder_id}")
        
        # Obter token
        access_token = obter_token(email, senha)
        
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        
        # Listar itens da pasta
        item_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{folder_id}/children"
        
        pastas = []
        arquivos = []
        
        # Suportar paginação
        while item_url:
            items_resp = requests.get(item_url, headers=headers, verify=False, timeout=30)
            
            if items_resp.status_code != 200:
                print(f"[ERRO] {items_resp.status_code}: {items_resp.text[:200]}")
                raise HTTPException(status_code=404, detail="Pasta não encontrada ou não tem permissão")
            
            data = items_resp.json()
            items = data.get("value", [])
            
            for item in items:
                if item.get("folder"):
                    pastas.append({
                        "id": item.get("id"),
                        "nome": item.get("name"),
                        "tipo": "pasta"
                    })
                else:
                    arquivos.append({
                        "id": item.get("id"),
                        "nome": item.get("name"),
                        "size": item.get("size", 0),
                        "drive_id": drive_id
                    })
            
            # Verificar se há mais páginas
            item_url = data.get("@odata.nextLink")
        
        print(f"[OK] {len(pastas)} pastas, {len(arquivos)} arquivos")
        
        return {
            "pastas": pastas,
            "arquivos": arquivos
        }
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/arquivos/{drive_id}/{item_id}/conteudo")
async def obter_conteudo_arquivo(drive_id: str, item_id: str, authorization: Optional[str] = Header(None)):
    """Obtém o conteúdo de um arquivo Excel"""
    try:
        email, senha = extrair_credenciais_token(authorization)
        print(f"[*] Obtendo arquivo: drive={drive_id}, item={item_id}")
        
        # Obter token
        access_token = obter_token(email, senha)
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/octet-stream"
        }
        
        # Baixar arquivo
        url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/content"
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Erro ao baixar arquivo")
        
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
            "headers": headers_list,
            "dados": dados,
            "total_linhas": len(dados)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERRO] {str(e)}")
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
