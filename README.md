# Navegador de Arquivos SharePoint

Aplicação simples para conectar, autenticar e explorar arquivos do Microsoft SharePoint Online e OneDrive. Permite navegação multi-nível em pastas e visualização de arquivos Excel.

## Características

- ✓ Autenticação com email e senha (MSAL + Microsoft Graph API)
- ✓ Listagem de grupos/sites SharePoint
- ✓ Navegação recursiva em pastas
- ✓ Suporte a paginação (>200 itens)
- ✓ Visualização de arquivos Excel (.xlsx)
- ✓ Interface web responsiva (HTML + CSS + JavaScript)
- ✓ Comunicação HTTPS com certificado auto-assinado

## Requisitos

- Python 3.8+
- Windows, macOS, ou Linux

## Instalação

```bash
# Clonar repositório
git clone https://github.com/usuario/sharepoint-file-navigator
cd sharepoint-file-navigator

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## Configuração

1. **Criar arquivo de credenciais:**
   ```bash
   cp credentials.json.template credentials.json
   ```

2. **Editar `credentials.json`:**
   ```json
   {
     "email": "seu.email@seudominio.com.br",
     "senha": "sua_senha_aqui"
   }
   ```

3. **Gerar certificados SSL (primeira vez):**
   ```bash
   # Certificados já estão inclusos, ou regenere:
   # openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
   ```

## Uso

```bash
# Ativar ambiente virtual (se não estiver)
venv\Scripts\activate

# Iniciar servidor HTTPS
python app.py
```

O aplicativo estará disponível em: **https://localhost:8443**

## Fluxo de Uso

1. **Login**: Digite email e senha corporativa
2. **Selecionar Site**: Escolha um grupo/site SharePoint
3. **Navegar**: Explore pastas e subpastas recursivamente
4. **Visualizar**: Abra arquivos Excel para ver dados em tabela

## Estrutura do Projeto

```
.
├── app.py                      # Backend FastAPI (API + autenticação)
├── index.html                  # Interface web (HTML)
├── style.css                   # Estilos (CSS)
├── credentials.json.template   # Template de credenciais
├── credentials.json            # Credenciais (gitignored)
├── requirements.txt            # Dependências Python
├── cert.pem                    # Certificado SSL (auto-assinado)
├── key.pem                     # Chave privada SSL
├── iniciar.bat                 # Script de inicialização (Windows)
└── README.md                   # Este arquivo
```

## API

### Autenticação
- **POST /api/token** - Cria sessão com email/senha
  - Retorna: `{ "token": "uuid" }`

### Sites
- **GET /api/sites** - Lista grupos/sites do usuário
  - Header: `Authorization: Bearer <token>`
  - Retorna: Array de `{ id, nome, mail, tipo }`

### Arquivos
- **GET /api/sites/{site_id}/arquivos** - Lista arquivos da raiz
  - Header: `Authorization: Bearer <token>`
  - Retorna: `{ drive_id, pastas[], arquivos[] }`

- **GET /api/pastas/{drive_id}/{folder_id}/conteudo** - Lista conteúdo de pasta
  - Header: `Authorization: Bearer <token>`
  - Retorna: `{ pastas[], arquivos[] }`

- **GET /api/arquivos/{drive_id}/{item_id}/conteudo** - Baixa e processa Excel
  - Header: `Authorization: Bearer <token>`
  - Retorna: `{ headers[], dados[], total_linhas }`

## Stack Tecnológico

**Backend:**
- FastAPI 0.104.1
- MSAL 1.26.0 (autenticação Azure AD)
- openpyxl 3.1.5 (leitura Excel)
- uvicorn[ssl] 0.24.0 (servidor HTTPS)

**Frontend:**
- HTML5
- CSS3 (Flexbox)
- JavaScript vanilla (Fetch API)

## Segurança

⚠️ **AVALIAÇÃO DE DESENVOLVIMENTO:**
- Usa certificado auto-assinado (usar certificado válido em produção)
- Armazena credenciais em sessão em memória (usar Redis/cache persistente em produção)
- Desativa validação SSL em certificados (apenas para teste com localhost)

**Para produção:**
1. Usar certificados válidos (Let's Encrypt)
2. Implementar refresh token rotation
3. Armazenar sessões em database/cache
4. Usar CORS restritivo
5. Adicionar rate limiting
6. Implementar logging e monitoramento

## Limitações

- Máximo 200 itens por página (paginação automática)
- Suporta apenas leitura de Excel
- Sem compressão de downloads
- Sem cache de resultados

## Troubleshooting

### "Porta 8443 já em uso"
```bash
# Matar processo na porta 8443 (Windows)
netstat -ano | findstr :8443
taskkill /PID <PID> /F
```

### "Credenciais inválidas"
- Verificar email e senha
- Verificar se está usando conta corporativa (não pessoal)
- Verificar se há restrições de acesso condicional

### "Arquivo não encontrado"
- Verificar se tem permissão no SharePoint
- Tentar explorar pasta por pasta

## Licença

MIT License

## Autor

Adriano A. Sousa

