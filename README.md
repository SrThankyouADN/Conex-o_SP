# Leitor de Arquivo SharePoint

Aplicação simples para ler arquivos Excel do SharePoint usando **autenticação OAuth2** com Microsoft Azure AD.

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

### 3. Fazer login

1. Clique no botão **"🔐 Login com Microsoft"**
2. Você será redirecionado para fazer login
3. Use suas credenciais corporativas Microsoft
4. Após autenticação, será redirecionado de volta automaticamente

### 4. Visualizar dados

O arquivo será carregado automaticamente após o login. Dados exibidos em uma tabela formatada.

### 5. Desconectar

Clique em "Desconectar" para fazer logout.

## Requisitos

- Python 3.8+
- Conexão com internet
- Conta Microsoft corporativa (Azure AD)
- Acesso ao SharePoint da organização

## Structure

```
.
├── app.py                # Backend FastAPI + OAuth2 + MSAL
├── index.html           # Frontend (OAuth2 login + table)  
├── style.css            # Estilos
├── requirements.txt      # Dependências
├── iniciar.bat          # Auto-setup Windows
└── credentials.json     # Credenciais (git-ignored)
```

## Parar aplicação

Pressione `Ctrl + C` no terminal ou feche a janela

## Troubleshooting

**Erro "Python não encontrado"**
- Instale Python de https://www.python.org

**Erro de certificado SSL no navegador**
- É normal ser auto-assinado, clique "Continuar mesmo assim"

**Login redireciona para erro**
- Verifique se você está conectado com conta Azure AD
- Se usar conta pessoal, ela não vai funcionar
- Marque "Add Python to PATH" durante instalação

**Erro de certificado SSL**
- Certificado auto-assinado é normal
- Clique em "Continuar" ou "Avançado" no navegador

**Erro "Arquivo não encontrado"**
- Verifique se o link está correto
- Certifique-se que o arquivo está compartilhado

**Erro "Acesso negado"**
- O link pode ter expirado
- Compartilhe o arquivo novamente e obtenha um novo link

## Estrutura

- `index.html` - Interface web
- `style.css` - Estilos
- `app.py` - Servidor backend
- `requirements.txt` - Dependências Python
- `iniciar.bat` - Script de inicialização

---

Desenvolvido para leitura de arquivos compartilhados do Microsoft 365 / SharePoint Online
