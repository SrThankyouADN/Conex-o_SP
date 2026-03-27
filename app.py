from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from io import BytesIO
import openpyxl
from office365.runtime.auth.client_credential import ClientCredential
from office365.sharepoint.client_context import ClientContext

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

# SharePoint config
SHAREPOINT_URL = "https://governosp.sharepoint.com"
SITE_URL = "https://governosp.sharepoint.com/teams/SECGOVERNO-SECOM_Data"
PASTA_CAMINHO = "001_SicomData/Miscelaneous/"
ARQUIVO_NOME = "testeConectorPython.xlsx"

@app.get("/")
async def root():
    return {"status": "OK"}

@app.post("/api/dados")
async def obter_dados(creds: CredenciaisRequest):
    try:
        # Validar entrada
        if not creds.email or not creds.senha:
            raise HTTPException(status_code=400, detail="Email e senha são obrigatórios")
        
        # Autenticar no SharePoint (User Credentials)
        ctx = ClientContext(SITE_URL).with_user_credentials(creds.email, creds.senha)
        
        # Testar conexão
        web = ctx.web.get().execute_query()
        
        # Obter arquivo da pasta
        pasta_url = f"/teams/SECGOVERNO-SECOM_Data/Shared Documents/{PASTA_CAMINHO}"
        file_item = ctx.web.get_file_by_server_relative_url(f"{pasta_url}{ARQUIVO_NOME}")
        
        # Ler arquivo em memória
        content = BytesIO()
        file_item.download(content).execute_query()
        content.seek(0)
        
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
        
        return {
            "sucesso": True,
            "headers": headers,
            "dados": dados,
            "total_linhas": len(dados)
        }
    
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Erro na autenticação ou leitura de arquivo: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8443, ssl_keyfile="key.pem", ssl_certfile="cert.pem")
