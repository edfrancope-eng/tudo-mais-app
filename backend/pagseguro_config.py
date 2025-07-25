"""
Configurações para integração com PagSeguro - Sistema de Cobrança Automática
"""

# Configurações dos planos com botões PagSeguro
PAGSEGURO_PLANS = {
    "monthly": {
        "name": "Plano Mensal",
        "price": 20.00,
        "currency": "BRL",
        "billing_cycle": "monthly",
        "button_url": "https://pag.ae/7_SMqntur/button",
        "button_html": '''<!-- INICIO DO BOTAO PAGBANK --><a href="https://pag.ae/7_SMqntur/button" target="_blank" title="Pagar com PagBank"><img src="//assets.pagseguro.com.br/ps-integration-assets/botoes/pagamentos/205x30-pagar.gif" alt="Pague com PagBank - é rápido, grátis e seguro!" /></a><!-- FIM DO BOTAO PAGBANK -->''',
        "features": [
            "5 produtos/serviços em destaque",
            "Chat com clientes",
            "Perfil completo",
            "Suporte por email"
        ],
        "max_items": 5
    },
    "semiannual": {
        "name": "Plano Semestral",
        "price": 15.00,
        "currency": "BRL",
        "billing_cycle": "semiannual",
        "button_url": "https://pag.ae/7_SMo96xM/button",
        "button_html": '''<!-- INICIO DO BOTAO PAGBANK --><a href="https://pag.ae/7_SMo96xM/button" target="_blank" title="Pagar com PagBank"><img src="//assets.pagseguro.com.br/ps-integration-assets/botoes/pagamentos/205x30-pagar.gif" alt="Pague com PagBank - é rápido, grátis e seguro!" /></a><!-- FIM DO BOTAO PAGBANK -->''',
        "features": [
            "10 produtos/serviços em destaque",
            "Sistema de avaliações com estrelas",
            "Chat com clientes",
            "Perfil completo",
            "Links compartilháveis",
            "Suporte prioritário"
        ],
        "max_items": 10,
        "savings": "Economia de R$ 105,00 no ano!"
    },
    "annual": {
        "name": "Plano Anual",
        "price": 110.00,
        "currency": "BRL",
        "billing_cycle": "annual",
        "button_url": "https://pag.ae/7_SMhvoQp/button",
        "button_html": '''<!-- INICIO DO BOTAO PAGBANK --><a href="https://pag.ae/7_SMhvoQp/button" target="_blank" title="Pagar com PagBank"><img src="//assets.pagseguro.com.br/ps-integration-assets/botoes/pagamentos/205x30-pagar.gif" alt="Pague com PagBank - é rápido, grátis e seguro!" /></a><!-- FIM DO BOTAO PAGBANK -->''',
        "features": [
            "25 produtos/serviços em destaque",
            "Sistema de avaliações com estrelas",
            "Chat com clientes",
            "Perfil completo",
            "Links compartilháveis",
            "Máxima visibilidade",
            "Suporte prioritário",
            "Relatórios de desempenho"
        ],
        "max_items": 25,
        "savings": "Economia de R$ 130,00 no ano!",
        "most_popular": True
    }
}

# Configurações de Webhook do PagSeguro
WEBHOOK_CONFIG = {
    "endpoint": "/webhook/pagseguro",
    "token": "SEU_TOKEN_WEBHOOK_AQUI",  # Será configurado no painel do PagSeguro
    "events": [
        "PAYMENT_APPROVED",
        "PAYMENT_CANCELLED", 
        "PAYMENT_REFUNDED",
        "SUBSCRIPTION_ACTIVATED",
        "SUBSCRIPTION_CANCELLED",
        "SUBSCRIPTION_SUSPENDED",
        "SUBSCRIPTION_REACTIVATED"
    ]
}

# Status de assinatura
SUBSCRIPTION_STATUS = {
    "PENDING": "pending",           # Aguardando pagamento
    "ACTIVE": "active",             # Ativa e funcionando
    "SUSPENDED": "suspended",       # Suspensa por falta de pagamento
    "CANCELLED": "cancelled",       # Cancelada pelo cliente
    "EXPIRED": "expired"            # Expirada
}

# Configurações de automação
AUTOMATION_CONFIG = {
    "grace_period_days": 3,         # Dias de carência após falha no pagamento
    "reminder_days": [7, 3, 1],     # Dias antes do vencimento para enviar lembretes
    "auto_suspend_after_days": 3,   # Suspender após X dias de atraso
    "auto_cancel_after_days": 30,   # Cancelar após X dias suspenso
    "email_notifications": True,
    "support_email": "tudomaisapp@hotmail.com"
}

def get_plan_config(plan_type):
    """Retorna configuração de um plano específico"""
    return PAGSEGURO_PLANS.get(plan_type)

def get_all_plans():
    """Retorna todos os planos disponíveis"""
    return PAGSEGURO_PLANS

def get_plan_price(plan_type):
    """Retorna o preço de um plano"""
    plan = PAGSEGURO_PLANS.get(plan_type)
    return plan["price"] if plan else 0

def get_plan_max_items(plan_type):
    """Retorna o limite de itens de um plano"""
    plan = PAGSEGURO_PLANS.get(plan_type)
    return plan["max_items"] if plan else 0

def calculate_savings(plan_type):
    """Calcula economia em relação ao plano mensal"""
    if plan_type == "monthly":
        return 0
    
    monthly_price = PAGSEGURO_PLANS["monthly"]["price"]
    plan_price = PAGSEGURO_PLANS[plan_type]["price"]
    
    if plan_type == "semiannual":
        monthly_total = monthly_price * 6
        savings = monthly_total - plan_price
    elif plan_type == "annual":
        monthly_total = monthly_price * 12
        savings = monthly_total - plan_price
    else:
        savings = 0
    
    return savings

# Mensagens automáticas para diferentes eventos
AUTOMATED_MESSAGES = {
    "payment_approved": {
        "subject": "🎉 Pagamento Aprovado - Bem-vindo ao Tudo Mais!",
        "body": """
Olá {user_name}!

Seu pagamento foi aprovado com sucesso! 

✅ Plano: {plan_name}
✅ Valor: R$ {amount}
✅ Próximo vencimento: {next_billing_date}

Sua conta já está ativa e você pode começar a usar todas as funcionalidades do Tudo Mais.

Acesse: {app_url}

Obrigado por escolher o Tudo Mais!

Equipe Tudo Mais
tudomaisapp@hotmail.com
        """
    },
    "payment_failed": {
        "subject": "⚠️ Problema com seu Pagamento - Tudo Mais",
        "body": """
Olá {user_name}!

Não conseguimos processar seu pagamento para o plano {plan_name}.

Isso pode ter acontecido por:
• Cartão sem limite
• Cartão vencido
• Dados incorretos

Para não perder o acesso, atualize seus dados de pagamento em:
{payment_update_url}

Você tem {grace_period} dias para regularizar antes que o acesso seja suspenso.

Precisa de ajuda? Entre em contato: tudomaisapp@hotmail.com

Equipe Tudo Mais
        """
    },
    "subscription_cancelled": {
        "subject": "Assinatura Cancelada - Tudo Mais",
        "body": """
Olá {user_name}!

Sua assinatura do Tudo Mais foi cancelada conforme solicitado.

• Seu acesso continuará ativo até: {expiry_date}
• Após essa data, sua conta será suspensa
• Seus dados serão mantidos por 90 dias

Mudou de ideia? Você pode reativar sua assinatura a qualquer momento em:
{reactivation_url}

Sentiremos sua falta!

Equipe Tudo Mais
tudomaisapp@hotmail.com
        """
    },
    "subscription_reactivated": {
        "subject": "🎉 Assinatura Reativada - Tudo Mais",
        "body": """
Olá {user_name}!

Que bom ter você de volta! Sua assinatura foi reativada com sucesso.

✅ Plano: {plan_name}
✅ Status: Ativo
✅ Próximo vencimento: {next_billing_date}

Todas as suas funcionalidades já estão liberadas novamente.

Bem-vindo de volta ao Tudo Mais!

Equipe Tudo Mais
tudomaisapp@hotmail.com
        """
    }
}

def get_automated_message(event_type, **kwargs):
    """Retorna mensagem automática formatada para um evento"""
    message_template = AUTOMATED_MESSAGES.get(event_type)
    if not message_template:
        return None
    
    return {
        "subject": message_template["subject"].format(**kwargs),
        "body": message_template["body"].format(**kwargs)
    }

