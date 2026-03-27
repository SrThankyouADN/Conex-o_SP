import ssl
import os
from pathlib import Path

def gerar_certificado():
    cert_path = Path("cert.pem")
    key_path = Path("key.pem")
    
    if cert_path.exists() and key_path.exists():
        print("[OK] Certificado já existe")
        return True
    
    try:
        # Importar após ter certeza que ssl está disponível
        import subprocess
        
        print("[*] Gerando certificado SSL auto-assinado...")
        
        # Tentar com OpenSSL do sistema
        result = subprocess.run([
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-keyout", "key.pem", "-out", "cert.pem",
            "-days", "365", "-nodes",
            "-subj", "/CN=localhost"
        ], capture_output=True, timeout=30)
        
        if result.returncode == 0:
            print("[OK] Certificado gerado com sucesso")
            return True
        else:
            print("[AVISO] OpenSSL não encontrado, usando fallback Python...")
            return gerar_com_cryptography()
    
    except Exception as e:
        print(f"[AVISO] Erro ao usar OpenSSL: {e}")
        return gerar_com_cryptography()

def gerar_com_cryptography():
    """Gerar certificado usando biblioteca cryptography (fallback)"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.backends import default_backend
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        import datetime
        
        print("[*] Gerando certificado com cryptography...")
        
        # Gerar chave privada
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Criar certificado auto-assinado
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(u"localhost"),
                x509.DNSName(u"127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256(), default_backend())
        
        # Salvar chave privada
        with open("key.pem", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Salvar certificado
        with open("cert.pem", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        print("[OK] Certificado gerado com sucesso")
        return True
    
    except Exception as e:
        print(f"[ERRO] Falha ao gerar certificado: {e}")
        return False

if __name__ == "__main__":
    exit(0 if gerar_certificado() else 1)
