"""
Configuração de Produção para HostGator
"""
import os

class ProductionConfig:
    # Configurações básicas
    SECRET_KEY = os.environ.get("SECRET_KEY") or "ALTERE_ESTA_CHAVE_SECRETA_PARA_PRODUCAO"
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "ALTERE_ESTA_CHAVE_JWT_PARA_PRODUCAO"
    
    # Configuração do banco de dados MySQL na HostGator
    # IMPORTANTE: Substitua pelos dados reais do seu cPanel
    DB_USERNAME = "SEU_CPANEL_tudomais_user"  # Ex: joao123_tudomais_user
    DB_PASSWORD = "SUA_SENHA_DO_BANCO"        # Senha que você criou
    DB_NAME = "SEU_CPANEL_tudomais_db"        # Ex: joao123_tudomais_db
    DB_HOST = "localhost"                     # Geralmente localhost na HostGator
    
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de upload
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Configurações de segurança
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configurações do PagSeguro
    PAGSEGURO_WEBHOOK_TOKEN = "SEU_TOKEN_WEBHOOK_PAGSEGURO"  # Configure no painel PagSeguro
    
    # Email de suporte
    SUPPORT_EMAIL = "tudomaisapp@hotmail.com"
    
    # URL base do aplicativo (substitua pelo seu domínio)
    BASE_URL = "https://app.seudominio.com.br"  # Ex: https://app.minhaempresa.com.br
    
    # Modo de debug (SEMPRE False em produção)
    DEBUG = False
    TESTING = False

# Função para gerar chaves secretas seguras
def generate_secret_key():
    """
    Execute este código localmente para gerar chaves secretas:
    
    import secrets
    print("SECRET_KEY:", secrets.token_urlsafe(32))
    print("JWT_SECRET_KEY:", secrets.token_urlsafe(32))
    """
    import secrets
    return secrets.token_urlsafe(32)

# Instruções de configuração
SETUP_INSTRUCTIONS = """
INSTRUÇÕES DE CONFIGURAÇÃO PARA PRODUÇÃO:

1. CHAVES SECRETAS:
   Execute localmente:
   >>> import secrets
   >>> print("SECRET_KEY:", secrets.token_urlsafe(32))
   >>> print("JWT_SECRET_KEY:", secrets.token_urlsafe(32))
   
   Substitua as chaves no arquivo ou configure como variáveis de ambiente.

2. BANCO DE DADOS:
   - DB_USERNAME: Nome completo do usuário MySQL (ex: joao123_tudomais_user)
   - DB_PASSWORD: Senha do usuário MySQL
   - DB_NAME: Nome completo do banco (ex: joao123_tudomais_db)
   
3. DOMÍNIO:
   - BASE_URL: URL completa do seu aplicativo (ex: https://app.minhaempresa.com.br)
   
4. PAGSEGURO:
   - PAGSEGURO_WEBHOOK_TOKEN: Token de segurança configurado no painel PagSeguro
   
5. VARIÁVEIS DE AMBIENTE (Recomendado):
   No cPanel, em "Setup Python App", adicione as variáveis:
   - SECRET_KEY=sua_chave_secreta_gerada
   - JWT_SECRET_KEY=sua_chave_jwt_gerada
   - DATABASE_URL=mysql+pymysql://usuario:senha@localhost/banco
   - PAGSEGURO_WEBHOOK_TOKEN=seu_token_webhook
"""

