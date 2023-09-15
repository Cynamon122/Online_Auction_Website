from shop import db
from datetime import datetime
import json


# Definicja modelu CustomerOrder
class CustomerOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    invoice = db.Column(db.String(20), unique=True, nullable=False)
    status = db.Column(db.String(20), default='none', nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('register.id'), unique=False, nullable=False)
    customer = db.relationship('Register', backref='customer_orders')
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    org_owner = db.Column(db.Integer, primary_key=True)

    # Funkcja repr do reprezentacji obiektu CustomerOrder w czytelny sposób
    def __repr__(self):
        return '<CustomerOrder %r>' % self.invoice


db.create_all()
