"""
Configurações para o modo Beta do Tudo Mais
"""
from datetime import datetime, timedelta

# Configurações do modo Beta
BETA_CONFIG = {
    "is_beta_mode": True,
    "beta_start_date": "2025-01-01",  # Data de início do beta
    "beta_message": "🚀 Versão Beta - Teste gratuito por tempo indeterminado!",
    "beta_features": {
        "unlimited_trial": True,
        "free_advertising": True,
        "all_features_enabled": True,
        "no_payment_required": True
    },
    "migration_notice": {
        "show_notice": True,
        "notice_frequency_days": 7,  # Mostrar aviso a cada 7 dias
        "message": "Em breve, o Tudo Mais sairá da versão Beta. Você será notificado sobre os planos pagos com antecedência."
    }
}

# Configurações de notificação para o administrador
ADMIN_NOTIFICATIONS = {
    "new_signup_sound": True,
    "new_report_sound": True,
    "daily_summary": True,
    "email_notifications": "tudomaisapp@hotmail.com"
}

# Configurações do QR Code para divulgação
QR_CODE_CONFIG = {
    "beta_url": "https://tudomais-beta.app",  # URL que será definida após deploy
    "qr_code_text": """
🎯 TUDO MAIS - VERSÃO BETA

📱 Teste GRÁTIS por tempo indeterminado!

✅ Cadastre sua empresa
✅ Anuncie produtos e serviços  
✅ Receba avaliações
✅ Chat com clientes
✅ Links compartilháveis

📲 Escaneie o QR Code ou acesse:
{url}

#TudoMais #Beta #Gratuito #Empresas #Serviços
    """,
    "social_media_text": """
🚀 NOVIDADE! Aplicativo TUDO MAIS em BETA!

📍 Guia completo de empresas e serviços
🆓 TESTE GRATUITO por tempo indeterminado
📱 Cadastre sua empresa AGORA!

Acesse: {url}

#TudoMais #Beta #Empresas #Serviços #Gratuito
    """
}

def is_beta_mode():
    """Verifica se o aplicativo está em modo beta"""
    return BETA_CONFIG["is_beta_mode"]

def get_beta_message():
    """Retorna a mensagem do modo beta"""
    return BETA_CONFIG["beta_message"]

def should_show_migration_notice(last_shown_date=None):
    """Verifica se deve mostrar o aviso de migração"""
    if not BETA_CONFIG["migration_notice"]["show_notice"]:
        return False
    
    if not last_shown_date:
        return True
    
    days_since_last = (datetime.now() - last_shown_date).days
    return days_since_last >= BETA_CONFIG["migration_notice"]["frequency_days"]

def get_migration_notice():
    """Retorna o aviso de migração"""
    return BETA_CONFIG["migration_notice"]["message"]

def get_qr_code_content(beta_url):
    """Gera o conteúdo para o QR Code"""
    return {
        "url": beta_url,
        "text": QR_CODE_CONFIG["qr_code_text"].format(url=beta_url),
        "social_text": QR_CODE_CONFIG["social_media_text"].format(url=beta_url)
    }

def get_beta_features():
    """Retorna as funcionalidades habilitadas no beta"""
    return BETA_CONFIG["beta_features"]

# Configurações especiais para usuários beta
BETA_USER_CONFIG = {
    "trial_period_days": None,  # Ilimitado no beta
    "max_items_monthly": 999,   # Sem limite no beta
    "max_items_semiannual": 999,
    "max_items_annual": 999,
    "enable_reviews": True,
    "enable_chat": True,
    "enable_favorites": True,
    "enable_share_links": True,
    "enable_image_upload": True
}

