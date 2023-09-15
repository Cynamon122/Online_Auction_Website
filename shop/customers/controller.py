import secrets
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from shop import app, db, bcrypt
from .forms import CustomerRegisterForm, CustomerLoginFrom
from .models import Register
from ..admin.models import CustomerOrder


# Trasa do rejestracji nowego klienta
@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        # Haszowanie hasła przed zapisaniem w bazie danych
        hash_password = bcrypt.generate_password_hash(form.password.data)

        # Tworzenie nowego rekordu klienta
        register = Register(
            name=form.name.data,
            username=form.username.data,
            email=form.email.data,
            password=hash_password,
            country=form.country.data,
            city=form.city.data,
            contact=form.contact.data,
            address=form.address.data,
            zipcode=form.zipcode.data
        )

        # Dodawanie klienta do sesji bazy danych
        db.session.add(register)

        # Wyświetlanie komunikatu o powodzeniu i przekierowanie do strony logowania
        flash(f'Welcome {form.name.data} Thank you for registering', 'success')
        db.session.commit()
        return redirect(url_for('customer_login'))

    # Wyświetlenie formularza rejestracji klienta
    return render_template('customer/register.html', form=form)


# Trasa do logowania klienta
@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    form = CustomerLoginFrom()
    if form.validate_on_submit():
        # Pobranie użytkownika na podstawie adresu e-mail
        user = Register.query.filter_by(email=form.email.data).first()

        # Sprawdzenie, czy hasło jest poprawne
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Zalogowanie użytkownika
            login_user(user)

            # Wyświetlenie komunikatu o pomyślnym zalogowaniu i przekierowanie na stronę główną
            flash('You are login now!', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))

        # Wyświetlenie komunikatu o nieprawidłowym adresie e-mail lub haśle
        flash('Incorrect email or password', 'danger')
        return redirect(url_for('customer_login'))

    # Wyświetlenie formularza logowania klienta
    return render_template('/customer/login.html', form=form)


# Trasa do wylogowywania klienta
@app.route('/customer/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('customer_login'))
