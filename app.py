from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from io import BytesIO
import openpyxl
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

# URL do arquivo compartilhado (hardcoded)
SHAREPOINT_FILE_URL = "https://governosp.sharepoint.com/:x:/r/teams/SECGOVERNO-SECOM_Data/Shared%20Documents/001_SicomData/Miscelaneous/testeConectorPython.xlsx?d=w02cbd2a2c5a24fc9835ffd9fa1c8bbaa&csf=1&web=1&e=W6cp6H"
SITE_URL = "https://governosp.sharepoint.com/teams/SECGOVERNO-SECOM_Data"
PASTA_URL = "/teams/SECGOVERNO-SECOM_Data/Shared Documents/001_SicomData/Miscelaneous/testeConectorPython.xlsx"

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
        
        # Autenticar no SharePoint
        credentials = UserCredential(email, senha)
        ctx = ClientContext(SITE_URL).with_credentials(credentials)
        
        # Testar conexão
        print("[*] Testando conexão...")
        web = ctx.web.get().execute_query()
        print(f"[OK] Conectado a: {web.properties['Title']}")
        
        # Obter arquivo
        print("[*] Buscando arquivo...")
        file_item = ctx.web.get_file_by_server_relative_url(PASTA_URL)
        
        # Ler arquivo em memória
        content = BytesIO()
        file_item.download(content).execute_query()
        content.seek(0)
        print("[OK] Arquivo baixado")
        
        # Processar Excel
        workbook = openpyxl.load_workbook(content)
        worksheet = workbook.active
        
        # Extrair dados (primeira linha é cabeçalho)
        headers = []
        dados = []
        
        for idx, row in enumerate(worksheet.iter_rows(values_only=True)):
            if row and any(cell is not None for cell in row):  # Ignorar linhas vazias
                if idx == 0:
                    headers = [str(cell) if cell else "" for cell in row]
                else:
                    row_dict = {headers[i]: str(row[i]) if row[i] is not None else "" 
                               for i in range(len(headers))}
                    dados.append(row_dict)
        
        print(f"[OK] Dados extraídos: {len(dados)} linhas, {len(headers)} colunas")
        
        return {
            "sucesso": True,
            "headers": headers,
            "dados": dados,
            "total_linhas": len(dados)
        }
    
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        erro_msg = str(e).lower()
        
        if "access denied" in erro_msg or "401" in erro_msg or "unauthorized" in erro_msg:
            raise HTTPException(status_code=401, detail="Credenciais inválidas ou acesso negado.")
        elif "not found" in erro_msg or "404" in erro_msg:
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

