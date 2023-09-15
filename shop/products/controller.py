import os
import secrets
from datetime import datetime, timedelta
import pytz

from flask import redirect, render_template, url_for, flash, request, session, current_app
from flask_login import login_required, current_user

from shop import db, app, photos, search

from .forms import Addproducts
from .models import Addproduct
from ..admin.models import CustomerOrder
from ..customers.models import Register


# Trasa do wyświetlenia produktów użytkownika
@app.route('/products')
@login_required
def products():
    products = Addproduct.query.filter_by(owner=current_user.id).all()
    return render_template('admin/products.html', title="Admin Page", products=products)


# Trasa do wyświetlenia wszystkich produktów
@app.route('/all_products')
@login_required
def all_products():
    products = Addproduct.query.all()
    return render_template('admin/all_products.html', title="Admin Page", products=products)


# Trasa do wyświetlenia wszystkich zamówień (dostępna tylko dla admina)
@app.route('/all_orders')
@login_required
def all_orders():
    if current_user.type != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    orders = CustomerOrder.query.all()

    return render_template('admin/all_orders.html', title="Admin Page", orders=orders)


# Trasa do wyświetlenia pojedynczego produktu
@app.route('/products/<int:id>', methods=['GET', 'POST'])
def single_page(id):
    product = Addproduct.query.get_or_404(id)
    return render_template('products/single_page.html', title="Single Product Page", product=product)


# Trasa do dodawania nowego produktu
@app.route('/addproduct', methods=['GET', 'POST'])
@login_required
def addproduct():
    form = Addproducts(request.form)
    if request.method == "POST":
        name = form.name.data
        price = form.price.data
        description = form.description.data

        owner = current_user.id

        tz = pytz.timezone('Europe/Warsaw')
        end_date = datetime.utcnow() + timedelta(days=7, hours=2)
        end_date = tz.localize(end_date)

        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        addproduct = Addproduct(name=name, price=price,
                                description=description, image_1=image_1,
                                image_2=image_2, image_3=image_3, owner=owner, end_date=end_date)

        db.session.add(addproduct)
        flash(f'The product {name} was added in database', 'success')
        db.session.commit()

        return redirect(url_for('products'))

    return render_template('products/addproduct.html', form=form, title='Add a Product')


# Trasa do usuwania produktu
@app.route('/deleteproduct/<int:id>', methods=["POST"])
@login_required
def deleteproduct(id):
    product = Addproduct.query.get_or_404(id)
    if request.method == 'POST':
        # Usuwanie zdjęć
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
        except Exception as error:
            print(error)

        # Usuwanie produktu
        db.session.delete(product)
        db.session.commit()
        flash(f'Auction for {product.name} has been canceled', 'success')
        return redirect(url_for('products'))


# Trasa do przeszukiwania produktów
@app.route('/search')
def search():
    searchword = request.args.get('q')
    products = Addproduct.query.msearch(searchword, fields=['name', 'description'])

    return render_template('products/search.html', products=products)


# Trasa do aktualizacji ceny produktu
@app.route('/update_price/<int:id>', methods=['POST'])
def update_price(id):
    new_price = float(request.form.get('new_price'))
    product = Addproduct.query.get(id)
    if new_price > product.price:
        product.price = new_price
        product.highest_bidder = current_user.id

        db.session.commit()

        flash('Your offer has been made!', 'success')
    else:
        flash('Offer must be higher than the current price', 'danger')
    return redirect(url_for('single_page', id=id))


# Trasa do usuwania elementu z koszyka
@app.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('getcart'))
    except Exception as e:
        print(e)
        return redirect(url_for('getcart'))
