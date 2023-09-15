from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_uploads import IMAGES, UploadSet, configure_uploads
import os
from flask_msearch import Search
from flask_login import LoginManager
from flask_migrate import Migrate

# Pobranie katalogu bazowego, w którym znajduje się ten plik
basedir = os.path.abspath(os.path.dirname(__file__))

# Inicjalizacja obiektu SQLAlchemy, który będzie zarządzać bazą danych
db = SQLAlchemy()

# Inicjalizacja aplikacji Flask
app = Flask(__name__)

# Przygotowanie kontekstu aplikacji
app.app_context().push()

# Konfiguracja ścieżki do bazy danych
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///myshop.db"

# Inicjalizacja bazy danych
db.init_app(app)

# Inicjalizacja modułu Bcrypt do hashowania haseł
bcrypt = Bcrypt(app)

# Inicjalizacja modułu wyszukiwania
search = Search()
search.init_app(app)

# Inicjalizacja modułu Flask-Migrate do obsługi migracji bazy danych
migrate = Migrate(app, db)

# Inicjalizacja migracji w kontekście aplikacji
with app.app_context():
    # Sprawdzenie, czy używana jest baza danych SQLite
    if db.engine.url.drivername == "sqlite":
        # Inicjalizacja migracji dla SQLite
        migrate.init_app(app, db, render_as_batch=True)
    else:
        # Inicjalizacja migracji
        migrate.init_app(app, db)

# Inicjalizacja modułu Flask-Login do zarządzania sesjami użytkowników
login_manager = LoginManager()
login_manager.init_app(app)

# Ustalenie nazwy widoku logowania
login_manager.login_view = 'customer_login'

# Ustalenie kategorii komunikatów o wymaganiu odświeżenia sesji
login_manager.needs_refresh_message_category = 'danger'

# Ustalenie komunikatu o konieczności logowania
login_manager.login_message = u"Please login first"

# Klucz aplikacji i klucz tajny CSRF
app.config.update(dict(
    SECRET_KEY="powerful secretkey",
    WTF_CSRF_SECRET_KEY="a csrf secret key"))

# Miejsce zapisywania zdjęć
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(basedir, 'static/images')

# Inicjalizacja zestawu przesyłanych plików dla zdjęć
photos = UploadSet('photos', IMAGES)

# Konfiguracja przesyłania plików w aplikacji
configure_uploads(app, photos)

# Importy kontrolerów z innych modułów
from shop.admin import controller
from shop.products import controller
from shop.customers import controller
