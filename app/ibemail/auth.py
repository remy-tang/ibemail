from flask import (Blueprint, current_app, flash, g, redirect, render_template,
                   url_for)
from flask_login import current_user, login_required, login_user, logout_user
from ibemail import db, login_manager
from ibemail.bf_ibe import IBEClient
from ibemail.forms import LoginForm, RegisterForm
from ibemail.models import User
from werkzeug.security import check_password_hash  # For password verification
from werkzeug.security import generate_password_hash

bp = Blueprint("auth", __name__)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@bp.route("/register", methods=("GET", "POST"))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        error = None

        if not email:
            error = "Email is required."
        elif not password:
            error = "Password is required."
        elif db.session.query(User).filter(User.email == email).count() != 0:
            error = f"User {email} is already registered."

        if error is not None:
            flash(error)
        else:
            user = User(email=email, password=generate_password_hash(password))
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():

    # Fetch all email addresses
    available_emails = [user.email for user in User.query.all()]

    if current_user.is_authenticated:
        return redirect(url_for("email.inbox"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            # Set the IBE client for the user
            get_ibe_client()
            return redirect(url_for("email.inbox"))
        else:
            flash(
                "Connexion échouée. Veuillez vérifier votre email et votre mot de passe.",
                "danger",
            )
    return render_template(
        "auth/login.html", form=form, available_emails=available_emails
    )


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


def get_ibe_client():
    """Retrieve or create an IBE client instance for the current user."""
    # Check if the IBE client is already loaded for this request
    if not hasattr(g, "ibe_client"):
        # Use current_user.get_id() to retrieve the user-specific client
        user_id = current_user.get_id()

        # Access the user-specific IBE client in app.config, or create a new one
        if "IBE_CLIENTS" not in current_app.config:
            current_app.config["IBE_CLIENTS"] = {}

        # Retrieve or create the IBE client for the specific user
        if user_id not in current_app.config["IBE_CLIENTS"]:
            pkg_entity = current_app.config["IBE_PKG"]
            client = IBEClient(
                current_user.email, current_app.config["IBE_PUBLIC_PARAMS"]
            )
            client.set_d_ID(pkg_entity.generate_private_key(current_user.email))
            current_app.config["IBE_CLIENTS"][user_id] = client

        # Set the client in g for quick access during this request
        g.ibe_client = current_app.config["IBE_CLIENTS"][user_id]

    return g.ibe_client
