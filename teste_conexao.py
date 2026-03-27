#!/usr/bin/env python3
import requests
import base64
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Carregar credenciais do arquivo JSON
with open('credentials.json', 'r') as f:
    creds = json.load(f)

email = creds['email']
senha = creds['senha']

print(f"[*] Testando conexão com: {email}")
print(f"[*] Senha: {'*' * (len(senha) - 2) + senha[-2:]}")

# URL do arquivo
url = "https://governosp.sharepoint.com/teams/SECGOVERNO-SECOM_Data/_api/web/GetFileByServerRelativeUrl('%2Fteams%2FSECGOVERNO-SECOM_Data%2FShared%20Documents%2F001_SicomData%2FMiscelaneous%2FtesteConectorPython.xlsx')/$value"

# Criar autenticação Basic
credentials = f"{email}:{senha}"
encoded = base64.b64encode(credentials.encode()).decode()
headers = {'Authorization': f'Basic {encoded}'}

try:
    print("[*] Enviando requisição...")
    response = requests.get(
        url,
        headers=headers,
        verify=False,
        timeout=30
    )
    
    print(f"[*] Status: {response.status_code}")
    
    if response.status_code == 200:
        print(f"[OK] Arquivo baixado! Tamanho: {len(response.content)} bytes")
        
        # Tentar processar como Excel
        from io import BytesIO
        import openpyxl
        
        excel_stream = BytesIO(response.content)
        workbook = openpyxl.load_workbook(excel_stream)
        worksheet = workbook.active
        
        print(f"[OK] Arquivo Excel válido!")
        print(f"[OK] Planilha ativa: {worksheet.title}")
        
        # Contar linhas
        row_count = 0
        for row in worksheet.iter_rows():
            row_count += 1
        
        print(f"[OK] Total de linhas: {row_count}")
        
    elif response.status_code == 401:
        print("[ERRO] 401 - Credenciais inválidas ou acesso negado")
        print(f"Resposta: {response.text[:200]}")
    elif response.status_code == 404:
        print("[ERRO] 404 - Arquivo não encontrado")
    else:
        print(f"[ERRO] Status {response.status_code}")
        print(f"Resposta: {response.text[:200]}")
        
except Exception as e:
    print(f"[ERRO] Exceção: {type(e).__name__}")
    print(f"[ERRO] Mensagem: {str(e)}")
