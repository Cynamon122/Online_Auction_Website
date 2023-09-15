from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, PasswordField, SubmitField, validators, ValidationError

from .models import Register


# Formularz rejestracji klienta
class CustomerRegisterForm(FlaskForm):
    name = StringField('Name: ')
    username = StringField('Username: ', [validators.DataRequired()])
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message=' Both password must match! ')])
    confirm = PasswordField('Repeat Password: ', [validators.DataRequired()])
    country = StringField('Country: ', [validators.DataRequired()])
    city = StringField('City: ', [validators.DataRequired()])
    contact = StringField('Contact: ', [validators.DataRequired()])
    address = StringField('Address: ', [validators.DataRequired()])
    zipcode = StringField('Zip code: ', [validators.DataRequired()])

    profile = FileField('Profile', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Image only please')])
    submit = SubmitField('Register')

    # Walidacja nazwy użytkownika, sprawdzamy, czy nie jest zajęta
    def validate_username(self, username):
        if Register.query.filter_by(username=username.data).first():
            raise ValidationError('Username taken')

    # Walidacja adresu email, sprawdzamy, czy nie jest już w użyciu
    def validate_email(self, email):
        if Register.query.filter_by(email=email.data).first():
            raise ValidationError('Email already in use')


# Formularz logowania klienta
class CustomerLoginFrom(FlaskForm):
    email = StringField('Email: ', [validators.Email(), validators.DataRequired()])
    password = PasswordField('Password: ', [validators.DataRequired()])
