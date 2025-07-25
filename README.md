# Projeto Tudo Mais

Este é o repositório completo do aplicativo "Tudo Mais", um guia comercial e de serviços desenvolvido para conectar consumidores a empresas locais.

## Estrutura do Projeto

```
tudo_mais_app/
├── backend/                 # Código-fonte da API Flask (Python)
│   ├── app.py               # Aplicação principal Flask
│   ├── models.py            # Modelos do banco de dados
│   ├── routes.py            # Rotas da API
│   ├── pagseguro_config.py  # Configurações do PagSeguro
│   ├── webhook_handler.py   # Lógica para processar webhooks do PagSeguro
│   ├── requirements.txt     # Dependências Python
│   ├── config_production.py # Configurações para ambiente de produção
│   └── passenger_wsgi.py    # Arquivo WSGI para HostGator/Passenger
├── frontend/                # Código-fonte da interface React
│   ├── public/              # Arquivos estáticos (ícone, logo)
│   ├── src/                 # Componentes React, contextos, etc.
│   ├── package.json         # Dependências Node.js
│   └── build/               # (Gerado após `npm run build`) Versão otimizada para produção
├── docs/                    # Documentação do projeto
│   ├── GUIA_DEPLOY_HOSTGATOR.md # Guia passo a passo para deploy na HostGator
│   ├── MANUAL_DO_USUARIO.md     # Manual para anunciantes
│   ├── RESUMO_EXECUTIVO.md      # Visão geral do projeto
│   └── DOCUMENTACAO_TECNICA.md  # Documentação técnica detalhada
└── .htaccess                # Configurações do servidor web para HostGator
```

## Como Fazer o Deploy (HostGator cPanel)

Para colocar o aplicativo "Tudo Mais" online na HostGator usando o cPanel, siga o guia detalhado:

➡️ **[GUIA COMPLETO DE DEPLOY NA HOSTGATOR](docs/GUIA_DEPLOY_HOSTGATOR.md)**

Este guia irá cobrir:
1.  Configuração do Banco de Dados MySQL.
2.  Criação e configuração de Subdomínio.
3.  Upload dos arquivos do Backend (Flask) e Frontend (React Build).
4.  Configuração do ambiente Python (`Setup Python App`).
5.  Configuração dos Webhooks do PagSeguro.
6.  Configuração das variáveis de ambiente e migrações do banco de dados.

## Configurações Importantes para o Deploy

Antes de iniciar o deploy, você precisará configurar as seguintes informações no arquivo `backend/config_production.py` e/ou como variáveis de ambiente no cPanel (`Setup Python App`):

-   **Credenciais do Banco de Dados**: `DB_USERNAME`, `DB_PASSWORD`, `DB_NAME` (obtidas ao criar o banco no cPanel).
-   **Chaves Secretas**: `SECRET_KEY`, `JWT_SECRET_KEY` (gere chaves fortes e únicas).
-   **Token do Webhook PagSeguro**: `PAGSEGURO_WEBHOOK_TOKEN` (obtido no painel do PagSeguro).
-   **URL Base do Aplicativo**: `BASE_URL` (o subdomínio onde o app será acessado, ex: `https://app.seudominio.com.br`).

## Suporte

Para dúvidas e suporte, entre em contato através do email: `tudomaisapp@hotmail.com`

---

**Desenvolvido com excelência técnica e visão de negócio para o sucesso no mercado digital brasileiro.**

