import os
import secrets
import stripe
from flask import render_template, session, request, redirect, url_for, flash, jsonify, current_app
from flask_login import current_user, login_required
from shop import app, db, bcrypt, photos
from shop.products.models import Addproduct
from .models import CustomerOrder
from datetime import datetime

from ..products.forms import Addproducts


# Strona główna, wyświetla produkty, które nie zakończyły się jeszcze.
@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    products = Addproduct.query.filter(Addproduct.end_date > datetime.now()).paginate(page=page, per_page=8)
    return render_template('admin/home.html', title='Home Page', products=products)


# Funkcja do deklarowania zwycięzcy aukcji
@app.route('/declare_winner/<int:id>', methods=['POST'])
def declare_winner(id):
    product = Addproduct.query.get_or_404(id)

    # Sprawdzenie, czy już wybrano zwycięzcę
    if product.winner_id:
        return jsonify({'success': False, 'message': 'Winner already declared'})

    # Ustawienie zwycięzcy jako najwyższego licytującego
    product.winner_id = product.highest_bidder

    # Tworzenie nowego zamówienia
    product_id = product.id
    name = product.name
    price = product.price
    org_owner = product.owner
    invoice = secrets.token_hex(5)
    customer_id = product.winner_id
    status = 'Pending'  #status dla zakończonych zamówień
    order = CustomerOrder(product_id=product_id, name=name, price=price, org_owner=org_owner, invoice=invoice,
                          customer_id=customer_id, status=status)
    db.session.add(order)
    db.session.commit()

    return jsonify({'success': True, 'winner_id': product.winner_id})


# Strona wyświetlająca aukcje wygrane przez użytkownika
@app.route('/products_won')
@login_required
def products_won():
    products = CustomerOrder.query.filter_by(customer_id=current_user.id).all()
    return render_template('admin/products_won.html', title="Products won", products=products)


# Strona wyświetlająca aukcje sprzedane przez użytkownika
@app.route('/products_sold')
@login_required
def products_sold():
    orders = CustomerOrder.query.filter_by(org_owner=current_user.id).all()
    return render_template('admin/products_sold.html', title="Products sold", orders=orders)


# Aktualizacja statusu zamówienia przez administratora
@app.route('/update_order_status/<int:order_id>', methods=['POST'])
@login_required
def update_order_status(order_id):
    if current_user.type != 'Admin':
        flash('You do not have permission to update the order status.', 'danger')
        return redirect(url_for('home'))

    # Pobranie zamówienia do aktualizacji
    order = CustomerOrder.query.filter_by(id=order_id).first()

    if not order:
        flash('Order not found.', 'danger')
        return redirect(url_for('all_orders'))

    if request.method == 'POST':
        new_status = request.form.get('status')
        if new_status in ['Pending', 'Payment completed']:
            # Zaktualizuj status zamówienia
            order.status = new_status
            db.session.commit()
            flash('Order status updated successfully.', 'success')
        else:
            flash('Invalid status value.', 'danger')

    return redirect(url_for('all_orders'))


# Aktualizacja informacji o produkcie przez administratora
@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
@login_required
def updateproduct(id):
    if current_user.type != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    form = Addproducts(request.form)
    updateproduct = Addproduct.query.get_or_404(id)

    if request.method == "POST":
        updateproduct.name = form.name.data
        updateproduct.price = form.price.data
        updateproduct.description = form.description.data
        flash(f'The product {updateproduct.name} was updated', 'success')

        # Usunięcie obecnie zapisanego zdjęcia produktu i zapisanie nowego
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + updateproduct.image_1))
                updateproduct.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                updateproduct.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")

        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + updateproduct.image_2))
                updateproduct.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                updateproduct.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")

        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + updateproduct.image_3))
                updateproduct.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                updateproduct.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        db.session.commit()

        return redirect(url_for('products'))

    # Wypełnienie formularza danymi z bazy danych
    form.name.data = updateproduct.name
    form.price.data = updateproduct.price
    form.description.data = updateproduct.description

    return render_template('products/updateproduct.html', form=form, title='Update Product',
                           updateproduct=updateproduct)


# Funkcja do przetwarzania zamówienia
@app.route('/get_order')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        try:
            order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been sent successfully', 'success')
            return redirect(url_for('orders', invoice=invoice))

        except Exception as e:
            print(e)
            flash("Something went wrong", "danger")
            return redirect(url_for('getcart'))
