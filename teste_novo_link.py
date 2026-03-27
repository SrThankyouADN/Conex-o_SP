#!/usr/bin/env python3
import requests
from io import BytesIO
import openpyxl
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://governosp.sharepoint.com/:x:/r/teams/SECGOVERNO-SECOM_Data/Shared%20Documents/001_SicomData/Miscelaneous/testeConectorPython.xlsx?d=w02cbd2a2c5a24fc9835ffd9fa1c8bbaa&csf=1&web=1&e=GVgTTE"

print("[*] Testando novo link com expiração estendida...")
response = requests.get(url, verify=False, timeout=30, allow_redirects=True)

print(f"[*] Status: {response.status_code}")
print(f"[*] Content-Type: {response.headers.get('content-type', 'unknown')}")
print(f"[*] Tamanho: {len(response.content)} bytes")

if response.status_code == 200:
    try:
        wb = openpyxl.load_workbook(BytesIO(response.content))
        ws = wb.active
        headers = [str(cell.value) if cell.value else "" for cell in ws[1]]
        print(f"[OK] Arquivo Excel válido!")
        print(f"[OK] Cabeçalhos: {headers}")
        print("\n✓ SUCESSO! Link funciona e está acessível!")
    except Exception as e:
        print(f"[ERRO] Não é arquivo Excel: {str(e)}")
else:
    print(f"[ERRO] Status {response.status_code}")
    print(f"[ERRO] Conteúdo: {response.text[:200]}")
