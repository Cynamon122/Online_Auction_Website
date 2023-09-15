from sqlalchemy import DateTime

from shop import db
from datetime import datetime


# Klasa modelu reprezentującego produkty
class Addproduct(db.Model):
    __searchable__ = ['name', 'description']
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    pub_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    image_1 = db.Column(db.String(150), nullable=False, default='image1.jpg')
    image_2 = db.Column(db.String(150), nullable=True, default='image2.jpg')
    image_3 = db.Column(db.String(150), nullable=True, default='image3.jpg')

    owner = db.Column(db.Integer, nullable=False)
    highest_bidder = db.Column(db.Integer, nullable=False)
    end_date = db.Column(DateTime, nullable=False)
    winner_id = db.Column(db.Integer, nullable=True)

    def __repr__(self):
        return '<Post %r>' % self.name


db.create_all()
