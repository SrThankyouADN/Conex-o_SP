# Teste Conector SharePoint

Aplicação simples para testar conectividade com SharePoint usando credenciais Office365.

## Como usar

### 1. Primeiro acesso (ou após clonar o repositório)

Duplo-clique em `iniciar.bat`

Isso vai:
- Verificar instalação do Python
- Criar ambiente isolado
- Instalar dependências automaticamente
- Gerar certificado HTTPS
- Iniciar aplicação

### 2. Acessar a aplicação

Abra seu navegador em: **https://localhost:8443**

(Aviso de certificado é normal, clique em "Continuar mesmo assim")

### 3. Usar a aplicação

1. Digite seu email corporativo
2. Digite sua senha
3. Clique em "Conectar"
4. Os dados do arquivo serão exibidos em uma tabela

## Requisitos

- Python 3.8+
- OpenSSL (incluído no Windows 10+)

## Parar aplicação

Pressione `Ctrl + C` no terminal ou feche a janela

## Troubleshooting

**Erro "Python não encontrado"**
- Instale Python de https://www.python.org
- Marque "Add Python to PATH" durante instalação

**Erro de certificado SSL**
- Certificado auto-assinado é normal
- Clique em "Continuar" ou "Avançado" no navegador

**Erro "Arquivo não encontrado"**
- Verifique se arquivo existe em SharePoint no caminho correto
- Verifique credenciais Office365

## Estrutura

- `index.html` - Interface web
- `style.css` - Estilos
- `app.py` - Servidor backend
- `requirements.txt` - Dependências Python
- `iniciar.bat` - Script de inicialização

---

Desenvolvido para teste de conectividade com Microsoft 365 / SharePoint Online
