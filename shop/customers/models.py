from datetime import datetime

from shop import db, login_manager
from flask_login import UserMixin


# Funkcja do logowania użytkownika na podstawie jego ID
@login_manager.user_loader
def user_loader(user_id):
    return Register.query.get(user_id)


# Model użytkowników
class Register(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=False)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200), unique=False)
    country = db.Column(db.String(50), unique=False)
    city = db.Column(db.String(50), unique=False)
    contact = db.Column(db.String(50), unique=False)
    address = db.Column(db.String(50), unique=False)
    zipcode = db.Column(db.String(50), unique=False)
    profile = db.Column(db.String(200), unique=False, default='profile.jpg')
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type = db.Column(db.String(20), default='User', nullable=False)

    # Relacja do zamówień klienta
    orders = db.relationship('CustomerOrder', backref='customer_info')

    # Funkcja __repr__ zwraca reprezentację użytkownika w czytelny sposób
    def __repr__(self):
        return '<Register %r>' % self.name


db.create_all()