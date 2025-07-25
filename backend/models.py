from datetime import datetime, date
from app import db, bcrypt
from sqlalchemy import Enum
import enum

class UserType(enum.Enum):
    CONSUMER = "consumer"
    ADVERTISER = "advertiser"
    ADMIN = "admin"

class SubscriptionPlan(enum.Enum):
    TRIAL = "trial"
    MONTHLY = "monthly"
    BIANNUAL = "biannual"
    ANNUAL = "annual"

class AdScope(enum.Enum):
    CITY = "Minha Cidade"
    CITY_REGION = "Minha Cidade e Região"
    CITY_REGION_OTHER_STATES = "Minha Cidade, Região e Outros Estados"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    user_type = db.Column(Enum(UserType), nullable=False, default=UserType.CONSUMER)
    profile_picture = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    advertiser_profile = db.relationship("Advertiser", backref="user", uselist=False)
    reviews = db.relationship("Review", backref="user", lazy=True)
    favorites = db.relationship("Favorite", backref="user", lazy=True)
    reports_made = db.relationship("Report", foreign_keys="Report.reporter_id", backref="reporter", lazy=True)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class State(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(2), nullable=False, unique=True)  # Ex: SP, RJ
    
    cities = db.relationship("City", backref="state", lazy=True)

class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    state_id = db.Column(db.Integer, db.ForeignKey("state.id"), nullable=False)
    
    advertisers = db.relationship("Advertiser", backref="city", lazy=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(255), nullable=True)
    
    advertisers = db.relationship("Advertiser", backref="category", lazy=True)

class Advertiser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    business_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=False)
    website = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    logo = db.Column(db.String(255), nullable=True)
    
    # Dados pessoais para verificação de idade
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    birth_date = db.Column(db.Date, nullable=False)
    
    # Localização e Escopo de Anúncio
    city_id = db.Column(db.Integer, db.ForeignKey("city.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    ad_scope = db.Column(Enum(AdScope), nullable=False, default=AdScope.CITY)
    
    # Assinatura
    subscription_plan = db.Column(Enum(SubscriptionPlan), nullable=False, default=SubscriptionPlan.TRIAL)
    subscription_start = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_end = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    has_had_trial = db.Column(db.Boolean, default=False) # Para controlar o teste gratuito
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    items = db.relationship("Item", backref="advertiser", lazy=True, cascade="all, delete-orphan")
    reviews = db.relationship("Review", backref="advertiser", lazy=True)
    favorites = db.relationship("Favorite", backref="advertiser", lazy=True)
    reports_received = db.relationship("Report", foreign_keys="Report.advertiser_id", backref="advertiser", lazy=True)
    
    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
    
    @property
    def is_adult(self):
        return self.age >= 18
    
    @property
    def average_rating(self):
        if not self.reviews:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)
    
    @property
    def can_receive_reviews(self):
        return self.subscription_plan in [SubscriptionPlan.BIANNUAL, SubscriptionPlan.ANNUAL]
    
    @property
    def max_items(self):
        if self.subscription_plan == SubscriptionPlan.ANNUAL:
            return 25
        elif self.subscription_plan == SubscriptionPlan.MONTHLY:
            return 5 # Novo limite para plano mensal
        return 10 # Limite padrão para trial e semestral

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    advertiser_id = db.Column(db.Integer, db.ForeignKey("advertiser.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.String(50), nullable=True)  # String para permitir "A partir de R$ 50"
    image = db.Column(db.String(255), nullable=True)
    order = db.Column(db.Integer, default=0)  # Para ordenação personalizada
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    advertiser_id = db.Column(db.Integer, db.ForeignKey("advertiser.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1 a 5 estrelas
    comment = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraint para evitar múltiplas avaliações do mesmo usuário para o mesmo anunciante
    __table_args__ = (db.UniqueConstraint("user_id", "advertiser_id", name="unique_user_advertiser_review"),)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    advertiser_id = db.Column(db.Integer, db.ForeignKey("advertiser.id"), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Constraint para evitar favoritos duplicados
    __table_args__ = (db.UniqueConstraint("user_id", "advertiser_id", name="unique_user_advertiser_favorite"),)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    advertiser_id = db.Column(db.Integer, db.ForeignKey("advertiser.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_from_advertiser = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.relationship("User", foreign_keys=[sender_id], backref="sent_messages")
    advertiser = db.relationship("Advertiser", foreign_keys=[advertiser_id], backref="chat_messages")

class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reporter_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    advertiser_id = db.Column(db.Integer, db.ForeignKey("advertiser.id"), nullable=False)
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="pending") # pending, reviewed, resolved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)




class PlanPricing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plan_type = db.Column(Enum(SubscriptionPlan), nullable=False, unique=True)
    price = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), default="BRL")
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @staticmethod
    def get_price(plan_type):
        pricing = PlanPricing.query.filter_by(plan_type=plan_type, is_active=True).first()
        return pricing.price if pricing else 0.0

