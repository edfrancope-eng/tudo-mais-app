#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from models import User, Advertiser, UserType, SubscriptionPlan, db, Report, AdScope
from datetime import date, timedelta, datetime
from app import jwt
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # Validação de dados de entrada básicos
    if not all(key in data for key in ["email", "password", "name", "birth_date", "cpf", "business_name", "phone", "category_id", "city_id"]):
        return jsonify({"error": "Dados incompletos"}), 400

    # Verificação de idade
    try:
        birth_date_obj = date.fromisoformat(data["birth_date"])
        today = date.today()
        age = today.year - birth_date_obj.year - ((today.month, today.day) < (birth_date_obj.month, birth_date_obj.day))
        if age < 18:
            return jsonify({"error": "O anunciante deve ter 18 anos ou mais."}), 400
    except ValueError:
        return jsonify({"error": "Formato de data de nascimento inválido. Use AAAA-MM-DD."}), 400

    # Verificação se o email ou CPF já existem
    existing_user = User.query.filter_by(email=data["email"]).first()
    existing_advertiser = Advertiser.query.filter_by(cpf=data["cpf"]).first()
    if existing_user or existing_advertiser:
        # Verificação do uso do trial
        if existing_advertiser and existing_advertiser.has_had_trial:
             return jsonify({"error": "Este CPF já utilizou o período de teste gratuito."}), 409
        return jsonify({"error": "Email ou CPF já cadastrado."}), 409

    # Criação do usuário
    new_user = User(
        email=data["email"],
        name=data["name"],
        user_type=UserType.ADVERTISER
    )
    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.flush() # Para obter o ID do usuário antes do commit

    # Criação do perfil do anunciante
    new_advertiser = Advertiser(
        user_id=new_user.id,
        business_name=data["business_name"],
        description=data.get("description"),
        phone=data["phone"],
        website=data.get("website"),
        address=data.get("address"),
        cpf=data["cpf"],
        birth_date=birth_date_obj,
        city_id=data["city_id"],
        category_id=data["category_id"],
        ad_scope=data.get("ad_scope", AdScope.CITY),
        subscription_plan=SubscriptionPlan.TRIAL,
        subscription_end=datetime.utcnow() + timedelta(days=7),
        has_had_trial=True # Marca que o usuário iniciou o trial
    )
    db.session.add(new_advertiser)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Anunciante cadastrado com sucesso! Período de teste de 7 dias iniciado."}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email e senha são obrigatórios"}), 400

    # Acesso especial para o administrador
    if data["email"] == "edfrancope" and data["password"] == "ngc1987@":
        access_token = create_access_token(identity={
            "user_id": 0, # ID reservado para admin
            "user_type": "admin"
        })
        return jsonify(access_token=access_token), 200

    user = User.query.filter_by(email=data["email"]).first()

    if user and user.check_password(data["password"]):
        access_token = create_access_token(identity={
            "user_id": user.id,
            "user_type": user.user_type.value
        })
        return jsonify(access_token=access_token), 200

    return jsonify({"error": "Email ou senha inválidos"}), 401

advertiser_bp = Blueprint("advertiser_bp", __name__, url_prefix="/advertiser")

@advertiser_bp.route("/<int:advertiser_id>", methods=["GET"])
def get_advertiser(advertiser_id):
    advertiser = Advertiser.query.get_or_404(advertiser_id)
    return jsonify({
        "id": advertiser.id,
        "business_name": advertiser.business_name,
        "description": advertiser.description,
        "phone": advertiser.phone,
        "website": advertiser.website,
        "address": advertiser.address,
        "logo": advertiser.logo,
        "city": advertiser.city.name,
        "category": advertiser.category.name,
        "average_rating": advertiser.average_rating,
        "max_items": advertiser.max_items,
        "is_active": advertiser.is_active,
        "items": [{
            "id": item.id,
            "title": item.title,
            "description": item.description,
            "price": item.price,
            "image": item.image
        } for item in advertiser.items]
    }), 200

@advertiser_bp.route("/", methods=["GET"])
def search_advertisers():
    query = request.args.get("query")
    category_id = request.args.get("category_id")
    city_id = request.args.get("city_id")

    advertisers = Advertiser.query.filter_by(is_active=True)

    if query:
        advertisers = advertisers.filter(Advertiser.business_name.like(f"%{query}%") | Advertiser.description.like(f"%{query}%"))
    if category_id:
        advertisers = advertisers.filter_by(category_id=category_id)
    if city_id:
        advertisers = advertisers.filter_by(city_id=city_id)

    results = []
    for adv in advertisers.all():
        results.append({
            "id": adv.id,
            "business_name": adv.business_name,
            "description": adv.description,
            "phone": adv.phone,
            "logo": adv.logo,
            "city": adv.city.name,
            "category": adv.category.name,
            "average_rating": adv.average_rating
        })
    return jsonify(results), 200

@advertiser_bp.route("/<int:advertiser_id>", methods=["PUT"])
@jwt_required()
def update_advertiser(advertiser_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_id"] != advertiser_id and current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    data = request.get_json()
    advertiser = Advertiser.query.get_or_404(advertiser_id)

    if "business_name" in data: advertiser.business_name = data["business_name"]
    if "description" in data: advertiser.description = data["description"]
    if "phone" in data: advertiser.phone = data["phone"]
    if "website" in data: advertiser.website = data["website"]
    if "address" in data: advertiser.address = data["address"]
    if "logo" in data: advertiser.logo = data["logo"] # TODO: Implementar upload de imagem real
    if "city_id" in data: advertiser.city_id = data["city_id"]
    if "category_id" in data: advertiser.category_id = data["category_id"]
    if "ad_scope" in data: advertiser.ad_scope = AdScope[data["ad_scope"].upper()]

    try:
        db.session.commit()
        return jsonify({"message": "Anunciante atualizado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@advertiser_bp.route("/<int:advertiser_id>", methods=["DELETE"])
@jwt_required()
def delete_advertiser(advertiser_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_id"] != advertiser_id and current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    advertiser = Advertiser.query.get_or_404(advertiser_id)

    try:
        db.session.delete(advertiser)
        db.session.commit()
        return jsonify({"message": "Anunciante deletado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Rotas para Itens (Produtos/Serviços)
@advertiser_bp.route("/<int:advertiser_id>/items", methods=["POST"])
@jwt_required()
def add_item(advertiser_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_id"] != advertiser_id and current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    data = request.get_json()
    advertiser = Advertiser.query.get_or_404(advertiser_id)

    if not data or not data.get("title"):
        return jsonify({"error": "Título do item é obrigatório"}), 400

    if len(advertiser.items) >= advertiser.max_items:
        return jsonify({"error": f"Limite de itens atingido para o seu plano ({advertiser.max_items} itens)."}), 400

    new_item = Item(
        advertiser_id=advertiser.id,
        title=data["title"],
        description=data.get("description"),
        price=data.get("price"),
        image=data.get("image") # TODO: Implementar upload de imagem real
    )
    db.session.add(new_item)

    try:
        db.session.commit()
        return jsonify({"message": "Item adicionado com sucesso!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@advertiser_bp.route("/items/<int:item_id>", methods=["PUT"])
@jwt_required()
def update_item(item_id):
    current_user_identity = get_jwt_identity()
    item = Item.query.get_or_404(item_id)
    if current_user_identity["user_id"] != item.advertiser.user_id and current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    data = request.get_json()

    if "title" in data: item.title = data["title"]
    if "description" in data: item.description = data["description"]
    if "price" in data: item.price = data["price"]
    if "image" in data: item.image = data["image"] # TODO: Implementar upload de imagem real

    try:
        db.session.commit()
        return jsonify({"message": "Item atualizado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@advertiser_bp.route("/items/<int:item_id>", methods=["DELETE"])
@jwt_required()
def delete_item(item_id):
    current_user_identity = get_jwt_identity()
    item = Item.query.get_or_404(item_id)
    if current_user_identity["user_id"] != item.advertiser.user_id and current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deletado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



# Rotas para Assinaturas
@advertiser_bp.route("/<int:advertiser_id>/subscribe", methods=["POST"])
@jwt_required()
def subscribe_advertiser(advertiser_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_id"] != advertiser_id and current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    data = request.get_json()
    if not data or not data.get("plan"):
        return jsonify({"error": "Plano de assinatura é obrigatório"}), 400

    try:
        new_plan = SubscriptionPlan[data["plan"].upper()]
    except KeyError:
        return jsonify({"error": "Plano de assinatura inválido."}), 400

    advertiser = Advertiser.query.get_or_404(advertiser_id)

    # Lógica de pagamento simulada
    # Em um ambiente real, aqui haveria a integração com um gateway de pagamento (Stripe, Mercado Pago, etc.)
    # e a confirmação do pagamento antes de atualizar o plano.
    payment_successful = True # Simulação

    if payment_successful:
        advertiser.subscription_plan = new_plan
        advertiser.subscription_start = datetime.utcnow()
        if new_plan == SubscriptionPlan.MONTHLY:
            advertiser.subscription_end = datetime.utcnow() + timedelta(days=30)
        elif new_plan == SubscriptionPlan.BIANNUAL:
            advertiser.subscription_end = datetime.utcnow() + timedelta(days=180)
        elif new_plan == SubscriptionPlan.ANNUAL:
            advertiser.subscription_end = datetime.utcnow() + timedelta(days=365)
        
        advertiser.is_active = True # Ativa o anunciante se ele estava inativo por falta de pagamento

        try:
            db.session.commit()
            return jsonify({"message": f"Assinatura atualizada para {new_plan.value} com sucesso!"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Pagamento falhou."}), 400

@advertiser_bp.route("/<int:advertiser_id>/cancel_subscription", methods=["POST"])
@jwt_required()
def cancel_subscription(advertiser_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_id"] != advertiser_id and current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    advertiser = Advertiser.query.get_or_404(advertiser_id)

    advertiser.subscription_plan = SubscriptionPlan.TRIAL # Ou um status de "cancelado" ou "pendente"
    advertiser.is_active = False # Desativa o anunciante ao cancelar a assinatura

    try:
        db.session.commit()
        return jsonify({"message": "Assinatura cancelada com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Rotas para o Painel Administrativo
admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def admin_dashboard():
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    total_users = User.query.count()
    total_advertisers = Advertiser.query.count()
    active_advertisers = Advertiser.query.filter_by(is_active=True).count()
    new_subscriptions_today = Advertiser.query.filter(Advertiser.subscription_start >= date.today()).count()
    pending_reports = Report.query.filter_by(status="pending").count()

    return jsonify({
        "total_users": total_users,
        "total_advertisers": total_advertisers,
        "active_advertisers": active_advertisers,
        "new_subscriptions_today": new_subscriptions_today,
        "pending_reports": pending_reports
    }), 200

@admin_bp.route("/advertisers", methods=["GET"])
@jwt_required()
def list_advertisers():
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    advertisers = Advertiser.query.all()
    results = []
    for adv in advertisers:
        results.append({
            "id": adv.id,
            "business_name": adv.business_name,
            "email": adv.user.email,
            "cpf": adv.cpf,
            "subscription_plan": adv.subscription_plan.value,
            "is_active": adv.is_active,
            "created_at": adv.created_at.isoformat()
        })
    return jsonify(results), 200

@admin_bp.route("/advertisers/<int:advertiser_id>/toggle_active", methods=["PUT"])
@jwt_required()
def toggle_advertiser_active(advertiser_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    advertiser = Advertiser.query.get_or_404(advertiser_id)
    advertiser.is_active = not advertiser.is_active
    try:
        db.session.commit()
        return jsonify({"message": "Status do anunciante atualizado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/advertisers/<int:advertiser_id>/delete", methods=["DELETE"])
@jwt_required()
def delete_advertiser_admin(advertiser_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    advertiser = Advertiser.query.get_or_404(advertiser_id)
    user = User.query.get_or_404(advertiser.user_id)
    try:
        db.session.delete(advertiser)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "Anunciante e usuário deletados permanentemente!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# Rotas para Denúncias
@admin_bp.route("/reports", methods=["GET"])
@jwt_required()
def list_reports():
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    reports = Report.query.filter_by(status="pending").all()
    results = []
    for report in reports:
        results.append({
            "id": report.id,
            "advertiser_name": report.advertiser.business_name,
            "reporter_email": report.reporter.email,
            "reason": report.reason,
            "created_at": report.created_at.isoformat()
        })
    return jsonify(results), 200

@admin_bp.route("/reports/<int:report_id>/resolve", methods=["PUT"])
@jwt_required()
def resolve_report(report_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    report = Report.query.get_or_404(report_id)
    report.status = "resolved"
    try:
        db.session.commit()
        return jsonify({"message": "Denúncia marcada como resolvida."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

user_bp = Blueprint("user_bp", __name__, url_prefix="/user")

@user_bp.route("/register", methods=["POST"])
def register_consumer():
    data = request.get_json()

    if not all(key in data for key in ["email", "password", "name"]):
        return jsonify({"error": "Email, senha e nome são obrigatórios"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email já cadastrado."}), 409

    new_user = User(
        email=data["email"],
        name=data["name"],
        user_type=UserType.CONSUMER
    )
    new_user.set_password(data["password"])
    db.session.add(new_user)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "Usuário consumidor cadastrado com sucesso!"}), 201

@user_bp.route("/<int:user_id>/favorites", methods=["POST"])
@jwt_required()
def add_favorite(user_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_id"] != user_id and current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    data = request.get_json()
    if not data or not data.get("advertiser_id"):
        return jsonify({"error": "ID do anunciante é obrigatório"}), 400

    user = User.query.get_or_404(user_id)
    advertiser = Advertiser.query.get_or_404(data["advertiser_id"])

    existing_favorite = Favorite.query.filter_by(user_id=user.id, advertiser_id=advertiser.id).first()
    if existing_favorite:
        return jsonify({"message": "Anunciante já está nos favoritos."}), 409

    new_favorite = Favorite(
        user_id=user.id,
        advertiser_id=advertiser.id
    )
    db.session.add(new_favorite)

    try:
        db.session.commit()
        return jsonify({"message": "Anunciante adicionado aos favoritos!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_bp.route("/<int:user_id>/favorites/<int:advertiser_id>", methods=["DELETE"])
@jwt_required()
def remove_favorite(user_id, advertiser_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_id"] != user_id and current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    favorite = Favorite.query.filter_by(user_id=user_id, advertiser_id=advertiser_id).first_or_404()

    try:
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({"message": "Anunciante removido dos favoritos!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_bp.route("/<int:user_id>/favorites", methods=["GET"])
@jwt_required()
def get_favorites(user_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_id"] != user_id and current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    user = User.query.get_or_404(user_id)
    favorites = []
    for fav in user.favorites:
        favorites.append({
            "id": fav.advertiser.id,
            "business_name": fav.advertiser.business_name,
            "logo": fav.advertiser.logo,
            "city": fav.advertiser.city.name,
            "category": fav.advertiser.category.name
        })
    return jsonify(favorites), 200

@user_bp.route("/<int:user_id>/reviews", methods=["POST"])
@jwt_required()
def add_review(user_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_id"] != user_id and current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    data = request.get_json()
    if not all(key in data for key in ["advertiser_id", "rating"]):
        return jsonify({"error": "ID do anunciante e avaliação são obrigatórios"}), 400

    advertiser = Advertiser.query.get_or_404(data["advertiser_id"])
    if not advertiser.can_receive_reviews:
        return jsonify({"error": "Este anunciante não pode receber avaliações."}), 400

    # TODO: Implementar filtro de palavras ofensivas para data["comment"]

    new_review = Review(
        user_id=user_id,
        advertiser_id=data["advertiser_id"],
        rating=data["rating"],
        comment=data.get("comment")
    )
    db.session.add(new_review)

    try:
        db.session.commit()
        return jsonify({"message": "Avaliação adicionada com sucesso!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_bp.route("/<int:user_id>/reviews/<int:review_id>", methods=["PUT"])
@jwt_required()
def update_review(user_id, review_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_id"] != user_id and current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    data = request.get_json()
    review = Review.query.get_or_404(review_id)

    if review.user_id != user_id:
        return jsonify({"error": "Você não tem permissão para editar esta avaliação."}), 403

    if "rating" in data: review.rating = data["rating"]
    if "comment" in data: review.comment = data["comment"] # TODO: Implementar filtro de palavras ofensivas

    try:
        db.session.commit()
        return jsonify({"message": "Avaliação atualizada com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_bp.route("/<int:user_id>/reviews/<int:review_id>", methods=["DELETE"])
@jwt_required()
def delete_review(user_id, review_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_id"] != user_id and current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    review = Review.query.get_or_404(review_id)

    if review.user_id != user_id:
        return jsonify({"error": "Você não tem permissão para deletar esta avaliação."}), 403

    try:
        db.session.delete(review)
        db.session.commit()
        return jsonify({"message": "Avaliação deletada com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_bp.route("/<int:user_id>/chat/<int:advertiser_id>", methods=["POST"])
@jwt_required()
def send_chat_message(user_id, advertiser_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_id"] != user_id and current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    data = request.get_json()
    if not data or not data.get("message"):
        return jsonify({"error": "Mensagem é obrigatória"}), 400

    # TODO: Implementar filtro de palavras ofensivas para data["message"]

    new_message = ChatMessage(
        sender_id=user_id,
        advertiser_id=advertiser_id,
        message=data["message"],
        is_from_advertiser=False # Mensagem enviada pelo consumidor
    )
    db.session.add(new_message)

    try:
        db.session.commit()
        return jsonify({"message": "Mensagem enviada com sucesso!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_bp.route("/<int:user_id>/chat/<int:advertiser_id>", methods=["GET"])
@jwt_required()
def get_chat_messages(user_id, advertiser_id):
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_id"] != user_id and current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    messages = ChatMessage.query.filter(
        ((ChatMessage.sender_id == user_id) & (ChatMessage.advertiser_id == advertiser_id)) |
        ((ChatMessage.sender_id == advertiser_id) & (ChatMessage.advertiser_id == user_id) & (ChatMessage.is_from_advertiser == True))
    ).order_by(ChatMessage.created_at).all()

    results = []
    for msg in messages:
        results.append({
            "id": msg.id,
            "sender_id": msg.sender_id,
            "advertiser_id": msg.advertiser_id,
            "message": msg.message,
            "is_from_advertiser": msg.is_from_advertiser,
            "created_at": msg.created_at.isoformat()
        })
    return jsonify(results), 200




# Rotas para gerenciamento de preços dos planos
@admin_bp.route("/pricing", methods=["GET"])
@jwt_required()
def get_plan_pricing():
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    pricing = PlanPricing.query.filter_by(is_active=True).all()
    results = []
    for p in pricing:
        results.append({
            "id": p.id,
            "plan_type": p.plan_type.value,
            "price": p.price,
            "currency": p.currency,
            "updated_at": p.updated_at.isoformat()
        })
    return jsonify(results), 200

@admin_bp.route("/pricing", methods=["POST"])
@jwt_required()
def update_plan_pricing():
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    data = request.get_json()
    if not data or not data.get("plan_type") or not data.get("price"):
        return jsonify({"error": "Tipo de plano e preço são obrigatórios"}), 400

    try:
        plan_type = SubscriptionPlan[data["plan_type"].upper()]
    except KeyError:
        return jsonify({"error": "Tipo de plano inválido"}), 400

    # Buscar ou criar o registro de preço
    pricing = PlanPricing.query.filter_by(plan_type=plan_type).first()
    if pricing:
        pricing.price = data["price"]
        pricing.updated_at = datetime.utcnow()
    else:
        pricing = PlanPricing(
            plan_type=plan_type,
            price=data["price"]
        )
        db.session.add(pricing)

    try:
        db.session.commit()
        return jsonify({"message": f"Preço do plano {plan_type.value} atualizado com sucesso!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Rota para Top 10 empresas mais recentes
@advertiser_bp.route("/top10", methods=["GET"])
def get_top10_recent():
    advertisers = Advertiser.query.filter_by(is_active=True).order_by(Advertiser.created_at.desc()).limit(10).all()
    
    results = []
    for adv in advertisers:
        # Pegar apenas os primeiros 3 itens para o resumo
        featured_items = adv.items[:3] if adv.items else []
        
        results.append({
            "id": adv.id,
            "business_name": adv.business_name,
            "description": adv.description[:150] + "..." if adv.description and len(adv.description) > 150 else adv.description,
            "logo": adv.logo,
            "city": adv.city.name,
            "state": adv.city.state.name,
            "category": adv.category.name,
            "average_rating": adv.average_rating,
            "phone": adv.phone,
            "website": adv.website,
            "featured_items": [{
                "id": item.id,
                "title": item.title,
                "price": item.price,
                "image": item.image
            } for item in featured_items],
            "created_at": adv.created_at.isoformat()
        })
    
    return jsonify(results), 200


# Importar configurações PagSeguro
from pagseguro_config import get_all_plans, get_plan_config, get_plan_price
# from webhook_handler import PagSeguroWebhookHandler
import os
from werkzeug.utils import secure_filename

# Configuração para upload de arquivos
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Rotas para sistema de pagamentos PagSeguro
@advertiser_bp.route("/plans", methods=["GET"])
def get_available_plans():
    """Retorna todos os planos disponíveis com botões PagSeguro"""
    plans = get_all_plans()
    
    # Adicionar informações de economia
    for plan_type, plan_data in plans.items():
        if plan_type != "monthly":
            monthly_price = plans["monthly"]["price"]
            if plan_type == "semiannual":
                monthly_equivalent = monthly_price * 6
                savings = monthly_equivalent - plan_data["price"]
                plan_data["monthly_equivalent"] = monthly_equivalent
                plan_data["savings_amount"] = savings
                plan_data["savings_percentage"] = round((savings / monthly_equivalent) * 100)
            elif plan_type == "annual":
                monthly_equivalent = monthly_price * 12
                savings = monthly_equivalent - plan_data["price"]
                plan_data["monthly_equivalent"] = monthly_equivalent
                plan_data["savings_amount"] = savings
                plan_data["savings_percentage"] = round((savings / monthly_equivalent) * 100)
    
    return jsonify(plans), 200

@advertiser_bp.route("/subscribe/<plan_type>", methods=["POST"])
@jwt_required()
def initiate_subscription(plan_type):
    """Inicia processo de assinatura - retorna dados do plano e botão PagSeguro"""
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_type"] != "advertiser":
        return jsonify({"error": "Não autorizado"}), 403

    plan_config = get_plan_config(plan_type)
    if not plan_config:
        return jsonify({"error": "Plano não encontrado"}), 404

    advertiser_id = current_user_identity["user_id"]
    advertiser = Advertiser.query.get(advertiser_id)
    if not advertiser:
        return jsonify({"error": "Anunciante não encontrado"}), 404

    # Preparar dados para o PagSeguro
    subscription_data = {
        "plan": plan_config,
        "user_email": advertiser.email,
        "user_name": advertiser.name,
        "reference_id": advertiser.email,  # Usado para identificar no webhook
        "redirect_url": f"{request.host_url}subscription-success",
        "notification_url": f"{request.host_url}webhook/pagseguro"
    }

    return jsonify(subscription_data), 200

# Webhook do PagSeguro
# Rota para webhook do PagSeguro

# @app.route("/webhook/pagseguro", methods=["POST"])
# def pagseguro_webhook():
#     """Recebe notificações automáticas do PagSeguro"""
#     # try:
#     #     # Verificar se é uma requisição válida
#     #     # signature = request.headers.get("X-PagSeguro-Signature")
#     #     # if not signature:
#     #     #     return jsonify({"error": "Assinatura não encontrada"}), 400
#     #
#     #     # webhook_data = request.get_json()
#     #     # if not webhook_data:
#     #     #     return jsonify({"error": "Dados não encontrados"}), 400
#     #
#     #     # # Validar a assinatura do PagSeguro
#     #     # # if not pagseguro_config.validate_signature(signature, request.data):
#     #     # #     return jsonify({"error": "Assinatura inválida"}), 403
#     #
#     #     # # Processar a notificação
#     #     # notification_code = webhook_data.get("notificationCode")
#     #     # notification_type = webhook_data.get("notificationType")
#     #
#     #     # if notification_type == "transaction":
#     #     #     # Buscar detalhes da transação no PagSeguro
#     #     #     transaction_details = pagseguro_config.get_transaction_details(notification_code)
#     #
#     #     #     if transaction_details:
#     #     #         transaction_status = transaction_details.get("status")
#     #     #         reference = transaction_details.get("reference")
#     #
#     #     #         # O reference deve ser o advertiser_id
#     #     #         if reference:
#     #     #             advertiser_id = int(reference)
#     #     #             advertiser = Advertiser.query.get(advertiser_id)
#     #
#     #     #             if advertiser:
#     #     #                 # Mapear status do PagSeguro para status internos
#     #     #                 if transaction_status == "PAID": # Exemplo: Pago
#     #     #                     # Ativar ou atualizar assinatura
#     #     #                     advertiser.is_active = True
#     #     #                     # Lógica para definir o plano e a data de expiração com base no produto/plano do PagSeguro
#     #     #                     # Por simplicidade, vamos assumir que a transação é para um plano mensal
#     #     #                     advertiser.subscription_plan = SubscriptionPlan.MONTHLY
#     #     #                     advertiser.subscription_start = datetime.utcnow()
#     #     #                     advertiser.subscription_end = datetime.utcnow() + timedelta(days=30)
#     #     #                     db.session.commit()
#     #     #                     print(f"Anunciante {advertiser_id} ativado/atualizado com sucesso.")
#     #     #                 elif transaction_status == "CANCELLED": # Exemplo: Cancelado
#     #     #                     advertiser.is_active = False
#     #     #                     db.session.commit()
#     #     #                     print(f"Anunciante {advertiser_id} desativado devido a cancelamento.")
#     #     #                 # Outros status como PENDING, IN_DISPUTE, etc.
#     #
#     #     # return jsonify(status="success"), 200
#     # except Exception as e:
#     #     db.session.rollback()
#     #     return jsonify({"error": str(e)}), 500
#         if not webhook_data:
#             return jsonify({"error": "Dados não encontrados"}), 400
#
#         # Processar webhook
#         result, status_code = PagSeguroWebhookHandler.process_webhook(webhook_data)
#         
#         return jsonify(result), status_code
#
#     except Exception as e:
#         return jsonify({"error": f"Erro no webhook: {str(e)}"}), 500

# Rota para verificar status da assinatura
@advertiser_bp.route("/subscription-status", methods=["GET"])
@jwt_required()
def get_subscription_status():
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_type"] != "advertiser":
        return jsonify({"error": "Não autorizado"}), 403

    advertiser_id = current_user_identity["user_id"]
    advertiser = Advertiser.query.get(advertiser_id)
    if not advertiser:
        return jsonify({"error": "Anunciante não encontrado"}), 404

    # Verificar se está no modo beta
    from beta_config import is_beta_mode
    if is_beta_mode():
        return jsonify({
            "status": "beta",
            "plan": "beta_unlimited",
            "is_active": True,
            "expires_at": None,
            "message": "Modo Beta - Acesso gratuito por tempo indeterminado"
        }), 200

    return jsonify({
        "status": advertiser.subscription_status,
        "plan": advertiser.subscription_plan.value if advertiser.subscription_plan else None,
        "is_active": advertiser.is_active,
        "expires_at": advertiser.trial_end_date.isoformat() if advertiser.trial_end_date else None,
        "last_payment_date": advertiser.last_payment_date.isoformat() if hasattr(advertiser, 'last_payment_date') and advertiser.last_payment_date else None,
        "last_payment_amount": float(advertiser.last_payment_amount) if hasattr(advertiser, 'last_payment_amount') and advertiser.last_payment_amount else None
    }), 200

# Rota para página de sucesso após pagamento
@app.route("/subscription-success", methods=["GET"])
def subscription_success():
    return jsonify({
        "message": "Pagamento processado! Você receberá uma confirmação por email em breve.",
        "redirect_url": f"{request.host_url}dashboard"
    }), 200

# Rotas para upload de imagens
@advertiser_bp.route("/upload-image", methods=["POST"])
@jwt_required()
def upload_image():
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_type"] != "advertiser":
        return jsonify({"error": "Não autorizado"}), 403

    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Adicionar timestamp para evitar conflitos
        timestamp = int(datetime.utcnow().timestamp())
        filename = f"{timestamp}_{filename}"
        
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Retornar URL relativa para o frontend
        image_url = f"/uploads/{filename}"
        
        return jsonify({
            "message": "Imagem enviada com sucesso",
            "image_url": image_url,
            "filename": filename
        }), 200
    
    return jsonify({"error": "Tipo de arquivo não permitido"}), 400

# Rota para servir imagens uploadadas
@advertiser_bp.route("/uploads/<filename>", methods=["GET"])
def serve_uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Rotas para sistema de chat
@user_bp.route("/chat/start", methods=["POST"])
@jwt_required()
def start_chat():
    current_user_identity = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get("advertiser_id"):
        return jsonify({"error": "ID do anunciante é obrigatório"}), 400

    # Verificar se já existe um chat entre estes usuários
    existing_chat = ChatMessage.query.filter_by(
        user_id=current_user_identity["user_id"],
        advertiser_id=data["advertiser_id"]
    ).first()

    if existing_chat:
        return jsonify({"message": "Chat já existe", "chat_id": existing_chat.id}), 200

    # Criar nova conversa
    chat = ChatMessage(
        user_id=current_user_identity["user_id"],
        advertiser_id=data["advertiser_id"],
        message="Conversa iniciada",
        sender_type="system",
        created_at=datetime.utcnow()
    )

    try:
        db.session.add(chat)
        db.session.commit()
        return jsonify({"message": "Chat iniciado", "chat_id": chat.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@user_bp.route("/chat/<int:chat_id>/messages", methods=["GET"])
@jwt_required()
def get_chat_messages(chat_id):
    current_user_identity = get_jwt_identity()
    
    messages = ChatMessage.query.filter_by(
        id=chat_id
    ).order_by(ChatMessage.created_at.asc()).all()

    if not messages:
        return jsonify({"error": "Chat não encontrado"}), 404

    # Verificar se o usuário tem acesso a este chat
    first_message = messages[0]
    if (current_user_identity["user_id"] != first_message.user_id and 
        current_user_identity["user_id"] != first_message.advertiser_id):
        return jsonify({"error": "Não autorizado"}), 403

    results = []
    for msg in messages:
        results.append({
            "id": msg.id,
            "message": msg.message,
            "sender_type": msg.sender_type,
            "created_at": msg.created_at.isoformat()
        })

    return jsonify(results), 200

@user_bp.route("/chat/<int:chat_id>/send", methods=["POST"])
@jwt_required()
def send_chat_message(chat_id):
    current_user_identity = get_jwt_identity()
    data = request.get_json()
    
    if not data or not data.get("message"):
        return jsonify({"error": "Mensagem é obrigatória"}), 400

    # Verificar se o chat existe e o usuário tem acesso
    existing_chat = ChatMessage.query.filter_by(id=chat_id).first()
    if not existing_chat:
        return jsonify({"error": "Chat não encontrado"}), 404

    if (current_user_identity["user_id"] != existing_chat.user_id and 
        current_user_identity["user_id"] != existing_chat.advertiser_id):
        return jsonify({"error": "Não autorizado"}), 403

    # Determinar tipo do remetente
    sender_type = "consumer" if current_user_identity["user_type"] == "consumer" else "advertiser"

    new_message = ChatMessage(
        user_id=existing_chat.user_id,
        advertiser_id=existing_chat.advertiser_id,
        message=data["message"],
        sender_type=sender_type,
        created_at=datetime.utcnow()
    )

    try:
        db.session.add(new_message)
        db.session.commit()
        return jsonify({"message": "Mensagem enviada", "message_id": new_message.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Rota para gerar link compartilhável
@advertiser_bp.route("/share-link", methods=["GET"])
@jwt_required()
def generate_share_link():
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_type"] != "advertiser":
        return jsonify({"error": "Não autorizado"}), 403

    advertiser_id = current_user_identity["user_id"]
    
    # Buscar dados do anunciante
    advertiser = Advertiser.query.get(advertiser_id)
    if not advertiser:
        return jsonify({"error": "Anunciante não encontrado"}), 404

    # Gerar link compartilhável
    base_url = request.host_url.rstrip('/')
    share_link = f"{base_url}/advertiser/{advertiser_id}"
    
    # Gerar texto para compartilhamento
    share_text = f"""
🏢 {advertiser.business_name}

📍 {advertiser.city.name}, {advertiser.city.state.name}
📱 {advertiser.phone}
{'🌐 ' + advertiser.website if advertiser.website else ''}

{advertiser.description[:100] + '...' if advertiser.description and len(advertiser.description) > 100 else advertiser.description or ''}

👆 Veja mais detalhes e entre em contato:
{share_link}

#TudoMais #Serviços #Local
    """.strip()

    return jsonify({
        "share_link": share_link,
        "share_text": share_text,
        "qr_code_url": f"{base_url}/api/qr-code?url={share_link}",
        "social_media": {
            "whatsapp": f"https://wa.me/?text={share_text.replace(' ', '%20')}",
            "telegram": f"https://t.me/share/url?url={share_link}&text={share_text.replace(' ', '%20')}",
            "facebook": f"https://www.facebook.com/sharer/sharer.php?u={share_link}",
            "twitter": f"https://twitter.com/intent/tweet?text={share_text.replace(' ', '%20')}"
        }
    }), 200


# Importar configurações beta
from beta_config import (
    is_beta_mode, get_beta_message, get_migration_notice, 
    get_qr_code_content, get_beta_features, BETA_USER_CONFIG
)
import qrcode
from io import BytesIO
import base64

# Rota para verificar status beta
@app.route("/api/beta-status", methods=["GET"])
def get_beta_status():
    return jsonify({
        "is_beta": is_beta_mode(),
        "message": get_beta_message(),
        "features": get_beta_features(),
        "migration_notice": get_migration_notice() if is_beta_mode() else None
    }), 200

# Rota para gerar QR Code
@app.route("/api/qr-code", methods=["GET"])
def generate_qr_code():
    url = request.args.get('url', request.host_url)
    
    # Gerar QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    
    # Criar imagem
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Converter para base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return jsonify({
        "qr_code": f"data:image/png;base64,{img_str}",
        "url": url,
        "content": get_qr_code_content(url)
    }), 200

# Rota para informações de divulgação beta
@admin_bp.route("/beta-promotion", methods=["GET"])
@jwt_required()
def get_beta_promotion_materials():
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403
    
    base_url = request.host_url.rstrip('/')
    qr_content = get_qr_code_content(base_url)
    
    return jsonify({
        "beta_url": base_url,
        "qr_code_api": f"{base_url}/api/qr-code?url={base_url}",
        "promotion_materials": {
            "qr_code_text": qr_content["text"],
            "social_media_text": qr_content["social_text"],
            "flyer_text": f"""
TUDO MAIS - VERSÃO BETA

O guia completo de empresas e serviços da sua região!

🆓 TESTE GRATUITO por tempo indeterminado
📱 Cadastre sua empresa
🌟 Receba avaliações
💬 Chat com clientes
📤 Links compartilháveis

Acesse: {base_url}
            """.strip()
        },
        "instructions": [
            "1. Use o QR Code em materiais impressos (cartazes, panfletos)",
            "2. Compartilhe o link nas redes sociais",
            "3. Envie por WhatsApp para empresários locais",
            "4. Divulgue em grupos de negócios",
            "5. Cole em estabelecimentos comerciais"
        ]
    }), 200

# Modificar rota de registro para modo beta
@auth_bp.route("/register", methods=["POST"])
def register_advertiser_beta():
    data = request.get_json()
    
    # Validações existentes...
    if not data or not all(k in data for k in ["email", "password", "name", "birth_date", "cpf", "business_name"]):
        return jsonify({"error": "Dados obrigatórios faltando"}), 400

    # Verificar idade (18+)
    try:
        birth_date = datetime.strptime(data["birth_date"], "%Y-%m-%d")
        age = (datetime.now() - birth_date).days // 365
        if age < 18:
            return jsonify({"error": "Cadastro permitido apenas para maiores de 18 anos"}), 400
    except ValueError:
        return jsonify({"error": "Data de nascimento inválida"}), 400

    # Verificar se CPF já existe (evitar múltiplos testes gratuitos)
    existing_cpf = Advertiser.query.filter_by(cpf=data["cpf"]).first()
    if existing_cpf:
        return jsonify({"error": "CPF já cadastrado. Cada CPF pode se cadastrar apenas uma vez."}), 400

    # Verificar se email já existe
    existing_email = Advertiser.query.filter_by(email=data["email"]).first()
    if existing_email:
        return jsonify({"error": "Email já cadastrado"}), 400

    # Hash da senha
    password_hash = bcrypt.generate_password_hash(data["password"]).decode('utf-8')

    # Criar novo anunciante
    new_advertiser = Advertiser(
        email=data["email"],
        password_hash=password_hash,
        name=data["name"],
        birth_date=birth_date,
        cpf=data["cpf"],
        business_name=data["business_name"],
        description=data.get("description", ""),
        phone=data.get("phone", ""),
        website=data.get("website", ""),
        address=data.get("address", ""),
        city_id=data.get("city_id", 1),
        category_id=data.get("category_id", 1),
        ad_scope=AdScope[data.get("ad_scope", "CITY")],
        is_active=True,
        created_at=datetime.utcnow()
    )

    # Configurar período de teste baseado no modo beta
    if is_beta_mode():
        # No modo beta, não há limite de tempo
        new_advertiser.trial_end_date = None
        new_advertiser.subscription_plan = SubscriptionPlan.TRIAL
        new_advertiser.subscription_status = "active"
        success_message = "Cadastro realizado com sucesso! Aproveite o teste GRATUITO por tempo indeterminado na versão Beta."
    else:
        # Modo normal: 7 dias de teste
        new_advertiser.trial_end_date = datetime.utcnow() + timedelta(days=7)
        new_advertiser.subscription_plan = SubscriptionPlan.TRIAL
        new_advertiser.subscription_status = "trial"
        success_message = "Cadastro realizado com sucesso! Período de teste de 7 dias iniciado."

    try:
        db.session.add(new_advertiser)
        db.session.commit()
        
        # TODO: Enviar notificação para admin sobre novo cadastro
        
        return jsonify({"message": success_message}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Rota para notificações do administrador
@admin_bp.route("/notifications", methods=["GET"])
@jwt_required()
def get_admin_notifications():
    current_user_identity = get_jwt_identity()
    if current_user_identity["user_type"] != "admin":
        return jsonify({"error": "Não autorizado"}), 403

    # Buscar notificações recentes
    today = datetime.utcnow().date()
    
    # Novos cadastros hoje
    new_signups_today = Advertiser.query.filter(
        db.func.date(Advertiser.created_at) == today
    ).count()
    
    # Novas denúncias pendentes
    pending_reports = Report.query.filter_by(status="pending").count()
    
    # Estatísticas gerais
    total_advertisers = Advertiser.query.count()
    active_advertisers = Advertiser.query.filter_by(is_active=True).count()
    
    return jsonify({
        "notifications": {
            "new_signups_today": new_signups_today,
            "pending_reports": pending_reports,
            "total_advertisers": total_advertisers,
            "active_advertisers": active_advertisers
        },
        "sounds_enabled": {
            "new_signup": True,
            "new_report": True
        },
        "beta_mode": is_beta_mode(),
        "last_updated": datetime.utcnow().isoformat()
    }), 200


#o


