from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from io import BytesIO
import openpyxl
import requests

app = FastAPI()

# CORS para aceitar requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str

def converter_url_para_download(url: str) -> str:
    """Converte URL do SharePoint para URL de download direto"""
    # Se já tem ?download=1, mantém
    if "?download=1" in url:
        return url
    
    # Formatos possíveis:
    # 1. URL normal: ...testeConectorPython.xlsx
    # 2. URL com ?web=1: ...testeConectorPython.xlsx?web=1
    # 3. URL com parâmetros: ...testeConectorPython.xlsx?d=w...
    
    # Adicionar ?download=1 para forçar download
    separator = "&" if "?" in url else "?"
    return url + f"{separator}download=1"

@app.get("/")
async def root():
    """Servir página principal"""
    return FileResponse("index.html", media_type="text/html")

@app.post("/api/dados")
async def obter_dados(request: URLRequest):
    try:
        # Validar entrada
        if not request.url or not request.url.strip():
            raise HTTPException(status_code=400, detail="URL do arquivo é obrigatória")
        
        url = request.url.strip()
        print(f"[*] URL recebida: {url}")
        
        # Converter para URL de download
        download_url = converter_url_para_download(url)
        print(f"[*] URL de download: {download_url}")
        
        # Baixar arquivo
        print("[*] Baixando arquivo...")
        response = requests.get(download_url, timeout=30)
        response.raise_for_status()
        print("[OK] Arquivo baixado")
        
        # Processar Excel
        content = BytesIO(response.content)
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
    
    except requests.exceptions.HTTPError as e:
        print(f"[ERRO] HTTP {e.response.status_code}: {e}")
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado. Verifique o link compartilhado.")
        elif e.response.status_code == 403:
            raise HTTPException(status_code=403, detail="Acesso negado. O link pode ter expirado ou não estar compartilhado.")
        else:
            raise HTTPException(status_code=400, detail=f"Erro HTTP {e.response.status_code}")
    
    except requests.exceptions.Timeout:
        print(f"[ERRO] Timeout ao baixar arquivo")
        raise HTTPException(status_code=408, detail="Timeout ao conectar. URL inacessível ou muito lenta.")
    
    except Exception as e:
        print(f"[ERRO] {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao processar arquivo: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("Iniciando servidor HTTPS")
    print("Acesse: https://localhost:8443")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8443, ssl_keyfile="key.pem", ssl_certfile="cert.pem")

