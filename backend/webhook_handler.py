"""
Handler para Webhooks do PagSeguro - Automação Completa de Assinaturas
"""

from flask import request, jsonify
from datetime import datetime, timedelta
import hashlib
import hmac
import json
from models import db, Advertiser, SubscriptionPlan
from pagseguro_config import (
    WEBHOOK_CONFIG, SUBSCRIPTION_STATUS, AUTOMATION_CONFIG,
    get_automated_message, get_plan_max_items
)

class PagSeguroWebhookHandler:
    
    @staticmethod
    def verify_webhook_signature(payload, signature, token):
        """Verifica se o webhook é realmente do PagSeguro"""
        expected_signature = hmac.new(
            token.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(signature, expected_signature)
    
    @staticmethod
    def process_webhook(webhook_data):
        """Processa o webhook recebido do PagSeguro"""
        try:
            event_type = webhook_data.get('eventType')
            reference_id = webhook_data.get('referenceId')  # Email do cliente
            
            if not event_type or not reference_id:
                return {"error": "Dados incompletos no webhook"}, 400
            
            # Buscar o anunciante pelo email (reference_id)
            advertiser = Advertiser.query.filter_by(email=reference_id).first()
            if not advertiser:
                return {"error": "Anunciante não encontrado"}, 404
            
            # Processar diferentes tipos de eventos
            if event_type == "PAYMENT_APPROVED":
                return PagSeguroWebhookHandler.handle_payment_approved(advertiser, webhook_data)
            
            elif event_type == "PAYMENT_CANCELLED":
                return PagSeguroWebhookHandler.handle_payment_failed(advertiser, webhook_data)
            
            elif event_type == "SUBSCRIPTION_ACTIVATED":
                return PagSeguroWebhookHandler.handle_subscription_activated(advertiser, webhook_data)
            
            elif event_type == "SUBSCRIPTION_CANCELLED":
                return PagSeguroWebhookHandler.handle_subscription_cancelled(advertiser, webhook_data)
            
            elif event_type == "SUBSCRIPTION_SUSPENDED":
                return PagSeguroWebhookHandler.handle_subscription_suspended(advertiser, webhook_data)
            
            elif event_type == "SUBSCRIPTION_REACTIVATED":
                return PagSeguroWebhookHandler.handle_subscription_reactivated(advertiser, webhook_data)
            
            else:
                return {"message": f"Evento {event_type} não processado"}, 200
                
        except Exception as e:
            return {"error": f"Erro ao processar webhook: {str(e)}"}, 500
    
    @staticmethod
    def handle_payment_approved(advertiser, webhook_data):
        """Processa pagamento aprovado - ATIVA a assinatura"""
        try:
            # Extrair informações do pagamento
            plan_info = webhook_data.get('planInfo', {})
            plan_type = plan_info.get('planType', 'monthly')
            amount = webhook_data.get('amount', 0)
            
            # Mapear tipo de plano
            plan_mapping = {
                'monthly': SubscriptionPlan.MONTHLY,
                'semiannual': SubscriptionPlan.SEMIANNUAL,
                'annual': SubscriptionPlan.ANNUAL
            }
            
            subscription_plan = plan_mapping.get(plan_type, SubscriptionPlan.MONTHLY)
            
            # Calcular data de vencimento
            if plan_type == 'monthly':
                next_billing = datetime.utcnow() + timedelta(days=30)
            elif plan_type == 'semiannual':
                next_billing = datetime.utcnow() + timedelta(days=180)
            elif plan_type == 'annual':
                next_billing = datetime.utcnow() + timedelta(days=365)
            else:
                next_billing = datetime.utcnow() + timedelta(days=30)
            
            # Atualizar dados do anunciante
            advertiser.subscription_plan = subscription_plan
            advertiser.subscription_status = SUBSCRIPTION_STATUS["ACTIVE"]
            advertiser.trial_end_date = next_billing
            advertiser.is_active = True
            advertiser.last_payment_date = datetime.utcnow()
            advertiser.last_payment_amount = amount
            
            db.session.commit()
            
            # Enviar email de confirmação
            PagSeguroWebhookHandler.send_automated_email(
                advertiser,
                "payment_approved",
                plan_name=plan_info.get('planName', 'Plano'),
                amount=f"{amount:.2f}",
                next_billing_date=next_billing.strftime('%d/%m/%Y')
            )
            
            return {"message": "Pagamento aprovado e assinatura ativada"}, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"Erro ao processar pagamento aprovado: {str(e)}"}, 500
    
    @staticmethod
    def handle_payment_failed(advertiser, webhook_data):
        """Processa falha no pagamento - INICIA período de carência"""
        try:
            # Definir período de carência
            grace_period_end = datetime.utcnow() + timedelta(
                days=AUTOMATION_CONFIG["grace_period_days"]
            )
            
            # Atualizar status (ainda não suspende imediatamente)
            advertiser.subscription_status = "payment_pending"
            advertiser.grace_period_end = grace_period_end
            
            db.session.commit()
            
            # Enviar email de aviso
            PagSeguroWebhookHandler.send_automated_email(
                advertiser,
                "payment_failed",
                plan_name=advertiser.subscription_plan.value,
                grace_period=AUTOMATION_CONFIG["grace_period_days"],
                payment_update_url="https://pagseguro.uol.com.br"  # URL do PagSeguro
            )
            
            return {"message": "Falha no pagamento processada, período de carência iniciado"}, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"Erro ao processar falha no pagamento: {str(e)}"}, 500
    
    @staticmethod
    def handle_subscription_activated(advertiser, webhook_data):
        """Processa ativação de assinatura (primeira vez ou reativação)"""
        return PagSeguroWebhookHandler.handle_payment_approved(advertiser, webhook_data)
    
    @staticmethod
    def handle_subscription_cancelled(advertiser, webhook_data):
        """Processa cancelamento de assinatura pelo cliente"""
        try:
            # Manter acesso até o fim do período pago
            expiry_date = advertiser.trial_end_date or datetime.utcnow()
            
            # Atualizar status
            advertiser.subscription_status = SUBSCRIPTION_STATUS["CANCELLED"]
            # Não desativa imediatamente, mantém até o vencimento
            
            db.session.commit()
            
            # Enviar email de confirmação do cancelamento
            PagSeguroWebhookHandler.send_automated_email(
                advertiser,
                "subscription_cancelled",
                expiry_date=expiry_date.strftime('%d/%m/%Y'),
                reactivation_url="https://tudomais.app/reativar"  # URL do seu app
            )
            
            return {"message": "Cancelamento processado"}, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"Erro ao processar cancelamento: {str(e)}"}, 500
    
    @staticmethod
    def handle_subscription_suspended(advertiser, webhook_data):
        """Processa suspensão por falta de pagamento"""
        try:
            # Suspender acesso
            advertiser.subscription_status = SUBSCRIPTION_STATUS["SUSPENDED"]
            advertiser.is_active = False
            
            db.session.commit()
            
            return {"message": "Assinatura suspensa"}, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"Erro ao processar suspensão: {str(e)}"}, 500
    
    @staticmethod
    def handle_subscription_reactivated(advertiser, webhook_data):
        """Processa reativação de assinatura"""
        try:
            # Reativar acesso
            advertiser.subscription_status = SUBSCRIPTION_STATUS["ACTIVE"]
            advertiser.is_active = True
            advertiser.grace_period_end = None
            
            # Calcular nova data de vencimento
            plan_type = advertiser.subscription_plan.value
            if plan_type == 'monthly':
                next_billing = datetime.utcnow() + timedelta(days=30)
            elif plan_type == 'semiannual':
                next_billing = datetime.utcnow() + timedelta(days=180)
            elif plan_type == 'annual':
                next_billing = datetime.utcnow() + timedelta(days=365)
            else:
                next_billing = datetime.utcnow() + timedelta(days=30)
            
            advertiser.trial_end_date = next_billing
            
            db.session.commit()
            
            # Enviar email de reativação
            PagSeguroWebhookHandler.send_automated_email(
                advertiser,
                "subscription_reactivated",
                plan_name=advertiser.subscription_plan.value,
                next_billing_date=next_billing.strftime('%d/%m/%Y')
            )
            
            return {"message": "Assinatura reativada"}, 200
            
        except Exception as e:
            db.session.rollback()
            return {"error": f"Erro ao processar reativação: {str(e)}"}, 500
    
    @staticmethod
    def send_automated_email(advertiser, event_type, **kwargs):
        """Envia email automático para o anunciante"""
        try:
            if not AUTOMATION_CONFIG["email_notifications"]:
                return
            
            message = get_automated_message(
                event_type,
                user_name=advertiser.name,
                app_url="https://tudomais.app",  # URL do seu app
                **kwargs
            )
            
            if message:
                # TODO: Implementar envio real de email
                # Por enquanto, apenas log
                print(f"EMAIL AUTOMÁTICO PARA {advertiser.email}:")
                print(f"Assunto: {message['subject']}")
                print(f"Corpo: {message['body']}")
                print("-" * 50)
                
        except Exception as e:
            print(f"Erro ao enviar email automático: {str(e)}")
    
    @staticmethod
    def check_expired_subscriptions():
        """Verifica e processa assinaturas expiradas (executar diariamente)"""
        try:
            now = datetime.utcnow()
            
            # Buscar assinaturas expiradas
            expired_advertisers = Advertiser.query.filter(
                Advertiser.trial_end_date <= now,
                Advertiser.subscription_status.in_([
                    SUBSCRIPTION_STATUS["ACTIVE"],
                    "payment_pending"
                ])
            ).all()
            
            for advertiser in expired_advertisers:
                if advertiser.subscription_status == "payment_pending":
                    # Suspender por falta de pagamento
                    advertiser.subscription_status = SUBSCRIPTION_STATUS["SUSPENDED"]
                    advertiser.is_active = False
                else:
                    # Expiração normal
                    advertiser.subscription_status = SUBSCRIPTION_STATUS["EXPIRED"]
                    advertiser.is_active = False
            
            db.session.commit()
            
            return len(expired_advertisers)
            
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao verificar assinaturas expiradas: {str(e)}")
            return 0

