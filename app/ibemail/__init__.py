import logging
import os
import pickle

from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CSRFProtect

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")

db = SQLAlchemy()
# Bootstrap-Flask requires this line
bootstrap = Bootstrap5()
# Flask-WTF requires this line
csrf = CSRFProtect()
# Flask-Login requires this line
login_manager = LoginManager()
# Flask-Mail requires this line
mail = Mail()


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # configure the SQLite database, relative to the app instance folder
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    with app.app_context():
        from .models import Email, User

        logger.debug("Creating tables")
        db.create_all()  # Create tables if they don't exist

    # Initialize the Bootstrap extension
    bootstrap.init_app(app)
    # Initialize the CSRF protection
    csrf.init_app(app)
    # Initialize the Mail extension
    mail.init_app(app)

    # Configure the mail server
    app.config["MAIL_SERVER"] = "mail.smtp2go.com"
    app.config["MAIL_PORT"] = 587
    app.config["MAIL_USE_SSL"] = False
    app.config["MAIL_USERNAME"] = SMTP_USER
    app.config["MAIL_PASSWORD"] = SMTP_PASS

    # Setup the login manager
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  # Redirect to this route if not logged in
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page."

    # Setup secret key
    import secrets

    foo = secrets.token_urlsafe(16)
    app.secret_key = foo

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
        logger.debug("Created instance folder")
    except OSError:
        pass

    # Add the auth blueprint
    from . import auth

    app.register_blueprint(auth.bp)

    # Add the email blueprint
    from . import email

    app.register_blueprint(email.bp)

    # Add the inbox route
    app.add_url_rule("/", endpoint="auth.login")

    # Setup the PKG, pickled and stored in the app context
    if "pkg.pickle" not in os.listdir(app.instance_path):
        from .pkg import PKG

        pkg_entity = PKG()
        pkg_entity.setup(512)
        public_params = pkg_entity.get_public_params()
        with open(os.path.join(app.instance_path, "pkg.pickle"), "wb") as f:
            pickle.dump((pkg_entity, public_params), f)
        logger.debug(f"Created PKG and stored in {app.instance_path}{os.sep}pkg.pickle")
    else:
        with open(os.path.join(app.instance_path, "pkg.pickle"), "rb") as f:
            pkg_entity, public_params = pickle.load(f)
        logger.debug(f"Loaded PKG from {app.instance_path}{os.sep}pkg.pickle")
    app.config["IBE_PKG"] = pkg_entity
    app.config["IBE_PUBLIC_PARAMS"] = public_params

    return app
