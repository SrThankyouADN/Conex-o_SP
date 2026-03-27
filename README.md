# Leitor de Arquivo OneDrive

Aplicação simples para ler arquivos Excel do OneDrive usando **autenticação por credenciais** com Microsoft Graph API.

## Como usar

### 1. Primeiro acesso (ou após clonar o repositório)

Duplo-clique em `iniciar.bat`

Isso vai:
- Verificar instalação do Python
- Criar ambiente isolado (venv)
- Instalar dependências automaticamente
- Gerar certificado HTTPS auto-assinado
- Iniciar servidor FastAPI

### 2. Acessar a aplicação

Abra seu navegador em: **https://localhost:8443**

(Aviso de certificado é normal - é auto-assinado, clique em "Continuar mesmo assim")

### 3. Autenticar

1. Digite seu **email corporativo** (ex: usuario@sp.gov.br)
2. Digite sua **senha**
3. Clique em **"Conectar"**

A aplicação fará autenticação não-interativa com a Microsoft e acessará seu OneDrive pessoal.

### 4. Visualizar dados

O arquivo será carregado automaticamente após autenticação. Dados exibidos em uma tabela formatada.

#### Arquivo acessado:
- **Localização**: OneDrive pessoal → `teste/testeConectorPython.xlsx`
- **Formato**: .xlsx (Excel)
- **Exibição**: Tabela HTML com headers e dados

## Requisitos

- Python 3.8+
- Conexão com internet
- Conta Microsoft corporativa (M365/Azure AD)
- Acesso ao OneDrive pessoal

## Estrutura

```
.
├── app.py                # Backend FastAPI + MSAL (não-interativo)
├── index.html           # Frontend (formulário email/senha + tabela)  
├── style.css            # Estilos CSS
├── requirements.txt      # Dependências Python
├── iniciar.bat          # Auto-setup Windows
└── credentials.json     # Template de credenciais (git-ignored)
```

## Parar aplicação

Pressione `Ctrl + C` no terminal ou feche a janela

## Troubleshooting

**Erro "Python não encontrado"**
- Instale Python de https://www.python.org

**Erro de certificado SSL no navegador**
- É normal ser auto-assinado, clique "Continuar mesmo assim"

**Erro "Credenciais inválidas"**
- Verifique email e senha
- Tente copiar/colar para evitar caracteres especiais
- Conta deve ser corporativa (Microsoft 365), não pessoal

**Erro "Arquivo não encontrado"**
- Verifique se o arquivo está em: `OneDrive/teste/testeConectorPython.xlsx`
- Verifique permissões de acesso

**Erro "Acesso bloqueado por Conditional Access"**
- Sua organização pode ter bloqueado autenticação não-interativa
- Contacte suporte da organização (SECOM/TI)
- Solicite exceção de Conditional Access para o aplicativo

**Erro "Erro de conexão / HTTPS"**
- Certificado auto-assinado é normal
- Clique em "Continuar" no navegador

## Notas de Segurança

- Credenciais são apenas armazenadas localmente (git-ignored)
- Não são transmitidas para servidor remoto
- Cada requisição obtém novo token da Microsoft
- HTTPS garante transmissão criptografada

---

Desenvolvido para leitura de arquivos do Microsoft 365 OneDrive
