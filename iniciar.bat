@echo off
chcp 65001 >nul
title Teste Conector SharePoint

echo.
echo ========================================
echo  Inicializando Aplicação
echo ========================================
echo.

REM Verificar se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python não está instalado ou não está no PATH
    echo Instale Python 3.8+ de https://www.python.org
    pause
    exit /b 1
)

echo [OK] Python encontrado

REM Criar venv se não existir
if not exist "venv" (
    echo [*] Criando ambiente virtual...
    python -m venv venv
    echo [OK] venv criado
) else (
    echo [OK] venv já existe
)

REM Ativar venv
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERRO] Falha ao ativar venv
    pause
    exit /b 1
)

echo [OK] venv ativado

REM Instalar dependências
echo [*] Instalando dependências...
echo.
pip install -r requirements.txt
echo.
if errorlevel 1 (
    echo [ERRO] Falha na instalação de dependências
    pause
    exit /b 1
)

echo [OK] Dependências instaladas

REM Gerar certificado HTTPS auto-assinado se não existir
if not exist "cert.pem" (
    echo [*] Gerando certificado SSL auto-assinado...
    python gerar_cert.py
    if errorlevel 1 (
        echo [ERRO] Falha ao gerar certificado.
        pause
        exit /b 1
    )
) else (
    echo [OK] Certificado já existe
)

echo.
echo ========================================
echo  Iniciando Servidor HTTPS
echo ========================================
echo.
echo Acesse: https://localhost:8443
echo (Aviso SSL é normal para certificado auto-assinado)
echo.
echo Pressione Ctrl+C para parar
echo.

REM Iniciar FastAPI
python app.py

pause
