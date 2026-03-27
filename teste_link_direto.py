#!/usr/bin/env python3
import requests
from io import BytesIO
import openpyxl
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Link direto do SharePoint
url = "https://governosp.sharepoint.com/:x:/r/teams/SECGOVERNO-SECOM_Data/Shared%20Documents/001_SicomData/Miscelaneous/testeConectorPython.xlsx?d=w02cbd2a2c5a24fc9835ffd9fa1c8bbaa&csf=1&web=1&e=Gjrc1W&nav=MTVfezAwMDAwMDAwLTAwMDEtMDAwMC0wMDAwLTAwMDAwMDAwMDAwMH0"

print("[*] Testando download via link direto...")
print(f"[*] URL: {url[:100]}...")

try:
    response = requests.get(
        url,
        verify=False,
        timeout=30,
        allow_redirects=True
    )
    
    print(f"[*] Status: {response.status_code}")
    print(f"[*] Content-Type: {response.headers.get('content-type', 'unknown')}")
    print(f"[*] Tamanho do conteúdo: {len(response.content)} bytes")
    
    if response.status_code == 200:
        # Tentar processar como Excel
        excel_stream = BytesIO(response.content)
        
        try:
            workbook = openpyxl.load_workbook(excel_stream)
            worksheet = workbook.active
            
            print(f"[OK] Arquivo Excel válido!")
            print(f"[OK] Planilha ativa: {worksheet.title}")
            
            # Extrair cabeçalhos
            headers = []
            for cell in worksheet[1]:
                headers.append(str(cell.value) if cell.value else "")
            
            print(f"[OK] Cabeçalhos: {headers}")
            
            # Contar linhas de dados
            row_count = 0
            for row in worksheet.iter_rows(min_row=2, values_only=True):
                if row and any(cell is not None for cell in row):
                    row_count += 1
            
            print(f"[OK] Total de linhas de dados: {row_count}")
            print("\n✓ SUCESSO! O link direto funciona e o arquivo é acessível!")
            
        except Exception as e:
            print(f"[ERRO] Não é um arquivo Excel válido")
            print(f"[ERRO] {str(e)}")
    else:
        print(f"[ERRO] Status {response.status_code}")
        print(f"[ERRO] Resposta: {response.text[:200]}")
        
except Exception as e:
    print(f"[ERRO] Exceção: {type(e).__name__}")
    print(f"[ERRO] Mensagem: {str(e)}")
