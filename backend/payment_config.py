"""
Configurações do sistema de pagamentos para o Tudo Mais
"""

# Informações bancárias do proprietário
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

# Configurações de PIX (PagSeguro suporta PIX)
PIX_CONFIG = {
    "pix_key": "215.887.058-38",  # CPF como chave PIX
    "pix_key_type": "CPF",
    "account_holder": "Edgard Franco Pereira"
}

# Instruções de pagamento para diferentes métodos
PAYMENT_INSTRUCTIONS = {
    "pix": {
        "title": "Pagamento via PIX",
        "description": "Transfira o valor exato usando a chave PIX abaixo:",
        "key": PIX_CONFIG["pix_key"],
        "key_type": "CPF",
        "instructions": [
            "1. Abra o app do seu banco",
            "2. Escolha a opção PIX",
            "3. Use a chave PIX: 215.887.058-38",
            "4. Confirme o valor exato do plano",
            "5. Envie o comprovante para tudomaisapp@hotmail.com"
        ]
    },
    "bank_transfer": {
        "title": "Transferência Bancária",
        "description": "Faça uma transferência para a conta abaixo:",
        "bank_details": {
            "bank": f"{PAYMENT_CONFIG['bank_name']} ({PAYMENT_CONFIG['bank_code']})",
            "agency": PAYMENT_CONFIG['agency'],
            "account": PAYMENT_CONFIG['account_number'],
            "holder": PAYMENT_CONFIG['account_holder'],
            "cpf": PAYMENT_CONFIG['cpf']
        },
        "instructions": [
            "1. Acesse seu internet banking",
            "2. Faça uma transferência para os dados acima",
            "3. Use como identificação: seu email cadastrado",
            "4. Envie o comprovante para tudomaisapp@hotmail.com"
        ]
    }
}

def get_payment_info(plan_type, amount):
    """
    Gera informações de pagamento para um plano específico
    """
    return {
        "plan_type": plan_type,
        "amount": amount,
        "currency": "BRL",
        "payment_methods": PAYMENT_INSTRUCTIONS,
        "support_email": PAYMENT_CONFIG["official_email"],
        "confirmation_required": True,
        "processing_time": "Até 24 horas após confirmação do pagamento"
    }

