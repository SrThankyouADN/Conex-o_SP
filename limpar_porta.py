#!/usr/bin/env python
"""Script para limpar executar app.py. Se houver erro de porta em uso, aguarda e tenta novamente."""

import subprocess
import time
import sys
import os

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    max_tentativas = 3
    tentativa = 0
    
    while tentativa < max_tentativas:
        tentativa += 1
        print(f"\n[*] Tentativa {tentativa}/{max_tentativas} de iniciar app.py...")
        
        try:
            # Executar app.py
            process = subprocess.Popen(
                [sys.executable, "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Ler primeira saída (startup)
            startup_ok = False
            for line in iter(process.stdout.readline, ''):
                if not line:
                    continue
                    
                print(line.rstrip())
                
                if "Application startup complete" in line:
                    startup_ok = True
                    print("\n✓ Servidor iniciado com sucesso!")
                    print(f"  Acesse: https://localhost:8443\n")
                    
                    # Manter o processo rodando
                    while True:
                        try:
                            line = process.stdout.readline()
                            if line:
                                print(line.rstrip())
                        except KeyboardInterrupt:
                            print("\n\n[*] Encerrando servidor...")
                            process.terminate()
                            process.wait(timeout=5)
                            return 0
                    
                elif "Address already in use" in line or "10048" in line:
                    print("\n[!] Porta 8443 em uso. Aguardando...")
                    process.terminate()
                    process.wait()
                    time.sleep(3)
                    break
                    
            if not startup_ok and process.poll() is not None:
                print("\n[!] Erro ao iniciar. Tentando novamente...\n")
                time.sleep(2)
                continue
                    
        except Exception as e:
            print(f"[ERRO] {e}")
            time.sleep(2)
    
    print("[ERRO] Não foi possível iniciar o servidor após várias tentativas.")
    return 1

if __name__ == "__main__":
    sys.exit(main())
