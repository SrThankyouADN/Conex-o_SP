# Leitor de Arquivo SharePoint

Aplicação simples para ler e exibir arquivos XLSX compartilhados no SharePoint usando link direto.

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

### 3. Obter o link do arquivo

1. Abra o SharePoint
2. Navegue até o arquivo XLSX
3. Clique com botão direito → **Compartilhar**
4. Configure para que o link seja acessível
5. Copie a URL do arquivo
6. Cole no campo da aplicação

### 4. Visualizar dados

1. Cole o link no campo "Link do Arquivo Compartilhado"
2. Clique em "Carregar Arquivo"
3. Os dados serão exibidos em uma tabela formatada

## Requisitos

- Python 3.8+

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
