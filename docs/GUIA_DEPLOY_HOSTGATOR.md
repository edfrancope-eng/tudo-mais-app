# Guia Completo de Deploy - Tudo Mais na HostGator

## Visão Geral

Este guia fornece instruções passo a passo para implantar o aplicativo "Tudo Mais" na HostGator usando o cPanel. O processo envolve configuração de subdomínio, banco de dados, upload de arquivos e configuração de webhooks.

## Pré-requisitos

- ✅ Conta ativa na HostGator com cPanel
- ✅ Domínio já configurado na HostGator
- ✅ Acesso ao cPanel da sua conta
- ✅ Arquivos do projeto "Tudo Mais" (fornecidos)
- ✅ Conta no PagSeguro para webhooks

## Estrutura Final Esperada

```
seu-dominio.com.br/
├── tudomais/                    # Aplicativo principal
│   ├── backend/                 # API Flask
│   ├── frontend/               # Interface React (build)
│   └── uploads/                # Arquivos enviados
└── public_html/                # Site principal (se existir)
```

---


## 1. Configuração do Banco de Dados (MySQL no cPanel)

O backend do "Tudo Mais" utiliza um banco de dados relacional. Na HostGator, você usará o MySQL via cPanel.

### 1.1. Criar Banco de Dados

1.  Acesse seu cPanel.
2.  Na seção **"Bancos de Dados"**, clique em **"Bancos de Dados MySQL®"**.
3.  Em **"Criar Novo Banco de Dados"**, digite um nome para o seu banco de dados (ex: `tudomais_db`) e clique em **"Criar Banco de Dados"**.
    *   **Anote o nome completo do banco de dados** (ele terá um prefixo, ex: `seucpanel_tudomais_db`).

### 1.2. Criar Usuário para o Banco de Dados

1.  Na mesma página **"Bancos de Dados MySQL®"**, role para baixo até a seção **"Usuários MySQL"**.
2.  Em **"Adicionar Novo Usuário"**, digite um nome de usuário (ex: `tudomais_user`) e uma senha forte.
3.  Clique em **"Criar Usuário"**.
    *   **Anote o nome completo do usuário** (ele também terá um prefixo, ex: `seucpanel_tudomais_user`) e a **senha**.

### 1.3. Adicionar Usuário ao Banco de Dados

1.  Ainda na página **"Bancos de Dados MySQL®"**, role para baixo até a seção **"Adicionar Usuário ao Banco de Dados"**.
2.  Selecione o **usuário** que você acabou de criar no campo **"Usuário"**.
3.  Selecione o **banco de dados** que você criou no campo **"Banco de Dados"**.
4.  Clique em **"Adicionar"**.
5.  Na próxima tela, marque a opção **"TODOS OS PRIVILÉGIOS"** e clique em **"Fazer Alterações"**.

---


## 2. Configuração de Subdomínio (para o Aplicativo)

É recomendado que o aplicativo rode em um subdomínio (ex: `app.seusite.com.br`) para separar do seu site principal.

### 2.1. Criar Subdomínio

1.  Acesse seu cPanel.
2.  Na seção **"Domínios"**, clique em **"Subdomínios"**.
3.  Em **"Criar um Subdomínio"**:
    *   No campo **"Subdomínio"**, digite o nome desejado (ex: `app`).
    *   Selecione seu domínio principal no menu suspenso.
    *   O campo **"Diretório Raiz do Documento"** será preenchido automaticamente (ex: `public_html/app`). Você pode alterá-lo para algo como `tudomais_app` para melhor organização, fora do `public_html` principal.
4.  Clique em **"Criar"**.

---


## 3. Upload de Arquivos e Configuração do Ambiente

Esta é a parte mais crítica, pois a HostGator (cPanel) tem algumas particularidades para aplicações Python/Node.js.

### 3.1. Upload dos Arquivos do Backend (Flask)

1.  **Acesse o Gerenciador de Arquivos do cPanel.**
2.  Navegue até o diretório raiz do seu subdomínio (ex: `tudomais_app` ou `app.seusite.com.br`).
3.  Crie uma pasta chamada `backend` dentro dela.
4.  **Compacte** todo o conteúdo da pasta `tudo_mais_app/backend` do seu projeto local (excluindo a pasta `venv` e `__pycache__`) em um arquivo `.zip`.
5.  Faça o upload deste `.zip` para a pasta `backend` no cPanel e **extraia** o conteúdo.
6.  **Edite o arquivo `app.py`** (ou o arquivo principal do seu Flask) para garantir que ele escute em `0.0.0.0` e na porta correta (geralmente a HostGator usa portas específicas ou você precisará de um arquivo `.htaccess` para redirecionamento).
    *   **Importante**: O cPanel da HostGator geralmente não permite que você rode um servidor Flask diretamente como um processo de longa duração. Você precisará usar a funcionalidade **"Setup Python App"** ou configurar um arquivo `.htaccess` para redirecionar requisições para um gateway WSGI (como `Passenger` ou `mod_wsgi`).

### 3.2. Configuração do Ambiente Python (Backend)

1.  No cPanel, procure por **"Setup Python App"** na seção **"Software"**.
2.  Clique em **"CREATE APPLICATION"**.
3.  Preencha os campos:
    *   **Python version**: Selecione a versão mais recente disponível (ex: `Python 3.9` ou superior).
    *   **Application root**: O caminho para a pasta `backend` que você criou (ex: `/home/seucpanel/tudomais_app/backend`).
    *   **Application URL**: O subdomínio que você criou (ex: `app.seusite.com.br`).
    *   **Application startup file**: `app.py` (ou o nome do seu arquivo principal Flask).
    *   **Application Entry point**: `app` (se sua instância Flask for `app = Flask(__name__)`).
    *   **Passenger Phusion**: Deixe como padrão.
4.  Clique em **"CREATE"**.
5.  Após a criação, o cPanel irá criar um ambiente virtual Python para você. Você precisará instalar as dependências do seu projeto.
    *   Na mesma tela do **"Setup Python App"**, role para baixo até a seção **"Configuration files"**.
    *   No campo **"Requirements file"**, adicione o caminho para o seu arquivo `requirements.txt` (que deve estar dentro da pasta `backend`).
    *   Clique em **"Add"** e depois em **"Run Pip Install"**.

### 3.3. Upload dos Arquivos do Frontend (React Build)

1.  **Gere a build de produção do seu aplicativo React localmente:**
    ```bash
    cd tudo_mais_app/frontend
    npm run build
    ```
    Isso criará uma pasta `build` (ou `dist`) dentro do seu diretório `frontend`.
2.  **Acesse o Gerenciador de Arquivos do cPanel.**
3.  Navegue até o diretório raiz do seu subdomínio (ex: `tudomais_app` ou `app.seusite.com.br`).
4.  Crie uma pasta chamada `frontend` dentro dela.
5.  **Compacte** todo o conteúdo da pasta `build` (ou `dist`) gerada pelo React em um arquivo `.zip`.
6.  Faça o upload deste `.zip` para a pasta `frontend` no cPanel e **extraia** o conteúdo.
7.  **Configuração do Servidor Web (Apache/Nginx via .htaccess):**
    *   Você precisará configurar o servidor web para servir os arquivos estáticos do frontend e redirecionar as requisições da API para o seu aplicativo Python.
    *   Crie ou edite o arquivo `.htaccess` na raiz do seu subdomínio (ex: `tudomais_app`).
    *   **Exemplo de `.htaccess` (pode variar dependendo da configuração exata da HostGator):**
        ```apache
        # Redireciona todas as requisições para o index.html do React
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteCond %{REQUEST_URI} !^/api/ # Exclui rotas da API
        RewriteRule . /frontend/index.html [L]

        # Redireciona requisições da API para o backend Flask
        RewriteRule ^api/(.*)$ http://127.0.0.1:SEU_PORTA_PYTHON/$1 [P,L]
        # Substitua SEU_PORTA_PYTHON pela porta que o Setup Python App gerou para você
        # ou use o Passenger WSGI para lidar com isso automaticamente.
        ```
    *   **Alternativa**: Se o `Setup Python App` da HostGator já lida com o proxy reverso, você pode apenas precisar configurar o `index.html` como o arquivo padrão para o subdomínio e garantir que as rotas da API sejam acessadas diretamente pelo domínio do backend.

---


## 4. Configuração dos Webhooks do PagSeguro

Para que o sistema de cobrança automática funcione, o PagSeguro precisa "avisar" seu aplicativo sobre os eventos de pagamento (aprovação, falha, cancelamento, etc.). Isso é feito via Webhooks.

### 4.1. Obter URL do Webhook

Sua URL de webhook será o endereço do seu aplicativo seguido de `/webhook/pagseguro`.

Exemplo: `https://app.seusite.com.br/webhook/pagseguro`

### 4.2. Configurar Webhook no PagSeguro

1.  Acesse sua conta no PagSeguro.
2.  Vá para a seção de **"Minha Conta"** ou **"Vendas"**.
3.  Procure por **"Notificações"** ou **"Webhooks"**.
4.  Adicione uma nova URL de notificação.
5.  Cole a URL do seu webhook (ex: `https://app.seusite.com.br/webhook/pagseguro`).
6.  **Importante**: O PagSeguro pode pedir um token de segurança. Você precisará configurar isso no seu backend (`pagseguro_config.py` e `webhook_handler.py`) e no painel do PagSeguro para garantir a segurança das notificações.

---


## 5. Configuração do Backend (Variáveis de Ambiente)

Você precisará atualizar o arquivo de configuração do seu backend (`tudo_mais_app/backend/config.py` ou similar) com as credenciais do banco de dados que você criou no cPanel.

### 5.1. Atualizar `config.py`

1.  Acesse o Gerenciador de Arquivos do cPanel.
2.  Navegue até a pasta `backend` do seu aplicativo.
3.  Edite o arquivo `config.py` (ou crie-o se ainda não existir) e adicione as seguintes variáveis:

    ```python
    import os

    class Config:
        SECRET_KEY = os.environ.get("SECRET_KEY") or "sua_chave_secreta_muito_forte"
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
            "mysql+pymysql://USUARIO_DB:SENHA_DB@localhost/NOME_DB"
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "sua_chave_jwt_secreta"
        UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
        MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limite para upload

    # Substitua pelos seus dados do cPanel
    # USUARIO_DB: Nome de usuário do banco de dados (ex: seucpanel_tudomais_user)
    # SENHA_DB: Senha do usuário do banco de dados
    # NOME_DB: Nome do banco de dados (ex: seucpanel_tudomais_db)
    ```

4.  **Importante**: Para o `SECRET_KEY` e `JWT_SECRET_KEY`, gere chaves aleatórias e complexas. Não use os exemplos acima em produção.

### 5.2. Executar Migrações do Banco de Dados

Após configurar o `SQLALCHEMY_DATABASE_URI`, você precisará executar as migrações para criar as tabelas no seu banco de dados MySQL.

1.  No cPanel, na seção **"Setup Python App"**, selecione seu aplicativo.
2.  Abaixo da seção **"Environment variables"**, você pode adicionar variáveis de ambiente se preferir não colocar as credenciais diretamente no `config.py`.
3.  Para executar as migrações, você precisará de acesso SSH ou de uma forma de executar comandos Python no seu ambiente. Se a HostGator permitir SSH, os comandos seriam:
    ```bash
    cd /home/seucpanel/tudomais_app/backend
    source venv/bin/activate
    flask db upgrade
    ```
    *   Se não tiver acesso SSH, você pode precisar de um script Python temporário que execute `db.create_all()` e depois removê-lo.

## 6. Testes e Considerações Finais

### 6.1. Testar o Backend (API)

-   Após o deploy do backend, tente acessar alguns endpoints da API (ex: `/auth/register`, `/advertiser/plans`) usando ferramentas como Postman ou Insomnia para verificar se estão respondendo corretamente.

### 6.2. Testar o Frontend

-   Acesse o subdomínio do seu aplicativo no navegador (ex: `https://app.seusite.com.br`).
-   Verifique se a interface carrega corretamente, se a logo aparece e se as funcionalidades básicas (cadastro, login) estão funcionando.

### 6.3. Testar Webhooks do PagSeguro

-   Faça um teste de compra real (ou use o modo sandbox do PagSeguro, se disponível) para verificar se os webhooks estão sendo recebidos e processados corretamente pelo seu backend.
-   Monitore os logs do seu servidor para ver as requisições de webhook.

### 6.4. Monitoramento e Manutenção

-   Monitore regularmente os logs do seu aplicativo para identificar erros.
-   Faça backups periódicos do seu banco de dados e dos arquivos de upload.
-   Mantenha suas dependências atualizadas.

### 6.5. Considerações de Segurança

-   Certifique-se de que todas as suas chaves secretas (`SECRET_KEY`, `JWT_SECRET_KEY`, token do webhook do PagSeguro) são únicas e não estão expostas publicamente.
-   Use HTTPS para todas as comunicações (a HostGator geralmente oferece SSL gratuito via Let's Encrypt).

---

Este guia cobre os passos essenciais para o deploy do "Tudo Mais" na HostGator. Lembre-se que cada ambiente de hospedagem pode ter suas particularidades, e pode ser necessário consultar a documentação específica da HostGator ou o suporte técnico deles para detalhes mais aprofundados.

