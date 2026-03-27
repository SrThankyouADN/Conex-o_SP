from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from io import BytesIO
import openpyxl
import requests

# URL do arquivo compartilhado (hardcoded)
SHAREPOINT_FILE_URL = "https://governosp.sharepoint.com/:x:/r/teams/SECGOVERNO-SECOM_Data/Shared%20Documents/001_SicomData/Miscelaneous/testeConectorPython.xlsx?d=w02cbd2a2c5a24fc9835ffd9fa1c8bbaa&csf=1&web=1&e=W6cp6H"

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
    # URL formato: https://governosp.sharepoint.com/:x:/r/teams/.../arquivo.xlsx?...
    # Precisa ser convertida para formato de download
    
    # Se contém /:x:/r/, converter para /teams/.../arquivo.xlsx?download=1
    if "/:x:/r/" in url:
        # Extrair a parte entre /r/ e os parâmetros
        parts = url.split("/:x:/r/")
        if len(parts) == 2:
            path_part = parts[1].split("?")[0]  # Remove parâmetros
            base_url = "https://governosp.sharepoint.com"
            # Retornar URL com ?download=1
            new_url = f"{base_url}/{path_part}?download=1"
            print(f"[*] URL convertida para: {new_url}")
            return new_url
    
    # Fallback: adicionar ?download=1 se não tiver
    if "?download=1" in url:
        return url
    
    separator = "&" if "?" in url else "?"
    return url + f"{separator}download=1"

@app.post("/api/dados")
async def obter_dados():
    try:
        url = SHAREPOINT_FILE_URL
        print(f"[*] Utilizando URL hardcoded")
        
        # Converter para URL de download
        download_url = converter_url_para_download(url)
        print(f"[*] URL de download: {download_url}")
        
        # Baixar arquivo com headers apropriados
        print("[*] Baixando arquivo...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        }
        response = requests.get(download_url, headers=headers, timeout=30, allow_redirects=True)
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

# Servir arquivos estáticos (CSS, JS, etc) - DEVE SER O ÚLTIMO
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("Iniciando servidor HTTPS")
    print("Acesse: https://localhost:8443")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8443, ssl_keyfile="key.pem", ssl_certfile="cert.pem")

