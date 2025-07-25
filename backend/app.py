from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
import os

# Importar a configuração de produção
from config_production import ProductionConfig

# Inicializar extensões sem app para configuração posterior
db = SQLAlchemy()
jwt = JWTManager()
bcrypt = Bcrypt()
cors = CORS()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Carregar configuração de produção
    app.config.from_object(ProductionConfig)

    # Inicializar extensões com o app
    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)

    # Importar e registrar blueprints
    from routes import auth_bp, advertiser_bp, admin_bp, user_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(advertiser_bp, url_prefix="/advertiser")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(user_bp, url_prefix="/user")

    # Importar modelos para que o Flask-Migrate os detecte
    from models import Advertiser, User, Report, SubscriptionPlan, PlanPricing, AdScope, ChatMessage

    return app

# Criar a instância do aplicativo
app = create_app()

# Adicionar rota de webhook diretamente ao app principal
from webhook_handler import PagSeguroWebhookHandler
@app.route("/webhook/pagseguro", methods=["POST"])
def pagseguro_webhook():
    try:
        # Verificar se é uma requisição válida
        signature = request.headers.get("X-PagSeguro-Signature")
        if not signature:
            return jsonify({"error": "Assinatura não encontrada"}), 400

        webhook_data = request.get_json()
        if not webhook_data:
            return jsonify({"error": "Dados não encontrados"}), 400

        # Processar webhook
        result, status_code = PagSeguroWebhookHandler.process_webhook(webhook_data)
        
        return jsonify(result), status_code

    except Exception as e:
        return jsonify({"error": f"Erro no webhook: {str(e)}"}), 500

# Rota para página de sucesso após pagamento
@app.route("/subscription-success", methods=["GET"])
def subscription_success():
    return jsonify({
        "message": "Pagamento processado! Você receberá uma confirmação por email em breve.",
        "redirect_url": f"{request.host_url}dashboard"
    }), 200

# Não rodar o app diretamente se estiver sendo importado pelo Passenger
if __name__ == "__main__":
    app.run(debug=True)


