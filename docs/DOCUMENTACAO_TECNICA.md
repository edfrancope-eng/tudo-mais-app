# Documentação Técnica - Tudo Mais

## Visão Geral do Projeto

O **Tudo Mais** é um aplicativo de guia comercial e de serviços desenvolvido para conectar consumidores a empresas locais. O projeto foi desenvolvido com arquitetura moderna, utilizando Flask para o backend e React para o frontend, com foco em escalabilidade, segurança e experiência do usuário.

## Arquitetura do Sistema

### Estrutura de Diretórios

```
tudo_mais_app/
├── backend/                 # Servidor Flask
│   ├── app.py              # Aplicação principal
│   ├── models.py           # Modelos de dados
│   ├── routes.py           # Rotas e endpoints
│   ├── payment_config.py   # Configurações de pagamento
│   ├── beta_config.py      # Configurações do modo beta
│   ├── venv/               # Ambiente virtual Python
│   └── uploads/            # Arquivos enviados pelos usuários
├── frontend/               # Aplicação React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── contexts/       # Contextos (Auth, etc.)
│   │   └── assets/         # Recursos estáticos
│   └── public/             # Arquivos públicos
└── docs/                   # Documentação
```

### Tecnologias Utilizadas

#### Backend
- **Flask 2.3+**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **Flask-JWT-Extended**: Autenticação JWT
- **Flask-Bcrypt**: Hash de senhas
- **Flask-CORS**: Suporte a CORS
- **QRCode**: Geração de códigos QR
- **Pillow**: Processamento de imagens

#### Frontend
- **React 18**: Biblioteca de interface
- **React Router**: Roteamento
- **Tailwind CSS**: Framework de estilos
- **Shadcn/UI**: Componentes de interface
- **Lucide React**: Ícones

#### Banco de Dados
- **SQLite** (desenvolvimento)
- **PostgreSQL** (produção recomendada)

## Modelos de Dados

### Principais Entidades

#### 1. Advertiser (Anunciante)
```python
class Advertiser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    business_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    phone = db.Column(db.String(20))
    website = db.Column(db.String(200))
    address = db.Column(db.String(300))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    ad_scope = db.Column(db.Enum(AdScope), default=AdScope.CITY)
    subscription_plan = db.Column(db.Enum(SubscriptionPlan), default=SubscriptionPlan.TRIAL)
    subscription_status = db.Column(db.String(20), default='trial')
    trial_end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### 2. User (Usuário Consumidor)
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    city_id = db.Column(db.Integer, db.ForeignKey('city.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### 3. Item (Produto/Serviço)
```python
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    advertiser_id = db.Column(db.Integer, db.ForeignKey('advertiser.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Decimal(10, 2))
    image_url = db.Column(db.String(300))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

#### 4. Review (Avaliação)
```python
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    advertiser_id = db.Column(db.Integer, db.ForeignKey('advertiser.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 estrelas
    comment = db.Column(db.Text)
    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

### Enumerações

#### Planos de Assinatura
```python
class SubscriptionPlan(Enum):
    TRIAL = "trial"
    MONTHLY = "monthly"
    SEMIANNUAL = "semiannual"
    ANNUAL = "annual"
```

#### Escopo de Anúncio
```python
class AdScope(Enum):
    CITY = "city"
    CITY_AND_REGION = "city_and_region"
    CITY_REGION_AND_STATES = "city_region_and_states"
```

## APIs e Endpoints

### Autenticação

#### POST /auth/register
Registra um novo anunciante.

**Parâmetros:**
```json
{
    "email": "string",
    "password": "string",
    "name": "string",
    "birth_date": "YYYY-MM-DD",
    "cpf": "string",
    "business_name": "string",
    "description": "string",
    "phone": "string",
    "website": "string",
    "address": "string",
    "city_id": "integer",
    "category_id": "integer",
    "ad_scope": "city|city_and_region|city_region_and_states"
}
```

**Validações:**
- Idade mínima: 18 anos
- CPF único (evita múltiplos cadastros)
- Email único

#### POST /auth/login
Autentica um usuário.

**Parâmetros:**
```json
{
    "email": "string",
    "password": "string",
    "user_type": "advertiser|consumer|admin"
}
```

**Resposta:**
```json
{
    "access_token": "string",
    "user": {
        "id": "integer",
        "name": "string",
        "email": "string",
        "user_type": "string"
    }
}
```

### Gerenciamento de Anunciantes

#### GET /advertiser/profile
Retorna o perfil do anunciante autenticado.

#### PUT /advertiser/profile
Atualiza o perfil do anunciante.

#### GET /advertiser/items
Lista os itens do anunciante.

#### POST /advertiser/items
Adiciona um novo item.

**Limites por plano:**
- Trial/Beta: Ilimitado
- Mensal: 5 itens
- Semestral: 10 itens
- Anual: 25 itens

#### POST /advertiser/upload-image
Faz upload de uma imagem.

**Formatos aceitos:** PNG, JPG, JPEG, GIF, WEBP

### Sistema de Pagamentos

#### GET /advertiser/payment-info/{plan_type}
Retorna informações de pagamento para um plano.

**Resposta:**
```json
{
    "plan_type": "string",
    "amount": "decimal",
    "currency": "BRL",
    "payment_methods": {
        "pix": {
            "title": "Pagamento via PIX",
            "key": "215.887.058-38",
            "key_type": "CPF",
            "instructions": ["array de instruções"]
        },
        "bank_transfer": {
            "title": "Transferência Bancária",
            "bank_details": {
                "bank": "PagSeguro Internet (290)",
                "agency": "0001",
                "account": "28911803-6",
                "holder": "Edgard Franco Pereira",
                "cpf": "215.887.058-38"
            }
        }
    }
}
```

#### POST /advertiser/confirm-payment
Confirma um pagamento realizado.

### Sistema de Avaliações

#### GET /advertiser/{id}/reviews
Lista as avaliações de um anunciante.

#### POST /advertiser/{id}/reviews
Adiciona uma nova avaliação (requer autenticação de consumidor).

**Parâmetros:**
```json
{
    "rating": "integer (1-5)",
    "comment": "string"
}
```

### Sistema de Favoritos

#### GET /user/favorites
Lista os favoritos do usuário.

#### POST /user/favorites/{advertiser_id}
Adiciona aos favoritos.

#### DELETE /user/favorites/{advertiser_id}
Remove dos favoritos.

### Painel Administrativo

#### GET /admin/dashboard
Retorna estatísticas do painel administrativo.

#### GET /admin/reports
Lista denúncias pendentes.

#### PUT /admin/reports/{id}
Atualiza status de uma denúncia.

#### GET /admin/plan-pricing
Lista preços dos planos.

#### PUT /admin/plan-pricing
Atualiza preços dos planos.

### Modo Beta

#### GET /api/beta-status
Retorna status do modo beta.

**Resposta:**
```json
{
    "is_beta": true,
    "message": "🚀 Versão Beta - Teste gratuito por tempo indeterminado!",
    "features": {
        "unlimited_trial": true,
        "free_advertising": true,
        "all_features_enabled": true,
        "no_payment_required": true
    },
    "migration_notice": "string"
}
```

#### GET /api/qr-code
Gera QR Code para divulgação.

**Parâmetros:**
- `url`: URL para o QR Code (opcional)

## Configurações

### Modo Beta

O aplicativo possui um sistema de configuração para modo beta localizado em `beta_config.py`:

```python
BETA_CONFIG = {
    "is_beta_mode": True,
    "beta_start_date": "2025-01-01",
    "beta_message": "🚀 Versão Beta - Teste gratuito por tempo indeterminado!",
    "beta_features": {
        "unlimited_trial": True,
        "free_advertising": True,
        "all_features_enabled": True,
        "no_payment_required": True
    }
}
```

### Pagamentos

As configurações de pagamento estão em `payment_config.py`:

```python
PAYMENT_CONFIG = {
    "bank_name": "PagSeguro Internet",
    "bank_code": "290",
    "agency": "0001",
    "account_number": "28911803-6",
    "account_type": "Conta de Pagamento",
    "cpf": "215.887.058-38",
    "account_holder": "Edgard Franco Pereira",
    "official_email": "tudomaisapp@hotmail.com"
}
```

## Segurança

### Autenticação
- JWT (JSON Web Tokens) para autenticação
- Senhas hasheadas com bcrypt
- Tokens com expiração configurável

### Validações
- Verificação de idade (18+) no cadastro
- CPF único para evitar múltiplos cadastros
- Validação de formatos de arquivo para upload
- Sanitização de dados de entrada

### Autorização
- Middleware de autorização por tipo de usuário
- Verificação de permissões em endpoints sensíveis
- Acesso administrativo restrito

## Performance

### Otimizações Implementadas
- Lazy loading de imagens
- Paginação em listas longas
- Cache de consultas frequentes
- Compressão de imagens

### Recomendações para Produção
- Usar CDN para arquivos estáticos
- Implementar cache Redis
- Configurar load balancer
- Monitoramento de performance

## Monitoramento

### Logs
- Logs de autenticação
- Logs de erros de API
- Logs de upload de arquivos
- Logs de pagamentos

### Métricas Recomendadas
- Número de usuários ativos
- Taxa de conversão de trial para pago
- Tempo de resposta das APIs
- Taxa de erro por endpoint

## Backup e Recuperação

### Estratégia de Backup
- Backup diário do banco de dados
- Backup semanal de arquivos de upload
- Versionamento de código no Git
- Documentação de procedimentos de recuperação

### Procedimentos de Recuperação
1. Restaurar banco de dados do backup mais recente
2. Restaurar arquivos de upload
3. Verificar integridade dos dados
4. Testar funcionalidades críticas

