from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from ibemail import db, logger
from ibemail.models import Email

from .auth import get_ibe_client
from .forms import EmailForm

bp = Blueprint("email", __name__)
from sage.all import Integer
from sage.schemes.elliptic_curves.ell_point import \
    EllipticCurvePoint_finite_field
from sqlalchemy.sql import text


@bp.route("/")
@login_required
def index():
    emails = db.session.execute(
        text(
            f"""SELECT e.id, sender, recipient, subject, timestamp, encrypted_body
            FROM email e 
            WHERE recipient = "{current_user.email}"
            ORDER BY timestamp 
            DESC
            """
        )
    ).fetchall()
    logger.info(f"Fetched {len(emails)} emails for {current_user.email}")
    return render_template("email/inbox.html", emails=emails)


@bp.route("/inbox")
@login_required
def inbox():
    emails = db.session.execute(
        text(
            f"""SELECT e.id, sender, recipient, subject, timestamp, encrypted_body
            FROM email e 
            WHERE recipient = "{current_user.email}"
            ORDER BY timestamp 
            DESC
            """
        )
    ).fetchall()
    logger.info(f"Fetched {len(emails)} emails for {current_user.email}")
    return render_template("email/inbox.html", emails=emails)


@bp.route("/sent")
@login_required
def sent_box():
    sent_emails = db.session.execute(
        text(
            f"""SELECT e.id, sender, recipient, subject, timestamp, encrypted_body
            FROM email e 
            WHERE sender = "{current_user.email}"
            ORDER BY timestamp 
            DESC
            """
        )
    ).fetchall()
    logger.info(f"Fetched {len(sent_emails)} sent emails for {current_user.email}")
    return render_template("email/sent_box.html", sent_emails=sent_emails)


@bp.route("/compose", methods=["GET", "POST"])
@login_required
def compose():
    from multiprocessing import Process, Queue

    form = EmailForm()
    client = get_ibe_client()

    if form.validate_on_submit():
        recipient = form.recipient.data
        subject = form.subject.data
        body = form.body.data

        # Encrypt email body using IBE
        encrypted_body = client.encrypt_from_address(body, recipient)
        # Format body
        formatted_encrypted_body = f"""x:{str(encrypted_body[0].x())}\ny:{str(encrypted_body[0].y())}\nV:{str(encrypted_body[1])}"""

        # Create a new email record
        email = Email(
            sender=current_user.email,
            recipient=recipient,
            subject=subject,
            encrypted_body=formatted_encrypted_body,
        )
        db.session.add(email)
        db.session.commit()

        logger.info(
            f"----- New email sent from {current_user.email} to {recipient} -----"
        )
        logger.info(f"From: {email.sender}")
        logger.info(f"To: {email.recipient}")
        logger.info(f"Subject: {email.subject}")
        logger.info(f"Encrypted body: {email.encrypted_body}")
        logger.info(f"----- End of email -----")
        flash("Email envoyé avec succès!", "success")
        return redirect(url_for("email.inbox"))
    return render_template("email/compose.html", title="Compose Email", form=form)


@bp.route("/email/<int:email_id>")
@login_required
def view_email(email_id):
    email = Email.query.get_or_404(email_id)
    # Decrypt email body
    logger.info(f"Viewing email {email_id} for {current_user.email}")
    return render_template(
        "email/view_email.html", email=email, current_user_email=current_user.email
    )


import re

from flask import jsonify


@bp.route("/email/<int:email_id>/decrypt")
@login_required
def decrypt_email(email_id):
    email = Email.query.get_or_404(email_id)
    client = get_ibe_client()
    logger.info(f"Deciphering email {email_id} for {current_user.email}")
    # Regular expression pattern to match "x:", "y:", and "V:" followed by a long integer
    pattern = r"x:(\d+)\ny:(\d+)\nV:(\d+)"

    # Use re.search to find the values
    match = re.search(pattern, email.encrypted_body)
    if match:
        x_value = match.group(1)  # Extracts the value after "x:"
        y_value = match.group(2)  # Extracts the value after "y:"
        V_value = match.group(3)  # Extracts the value after "V:"

        decrypted_body = client.decrypt(
            [
                EllipticCurvePoint_finite_field(
                    client.E, (Integer(int(x_value)), Integer(int(y_value)))
                ),
                int(V_value),
            ]
        )
        logger.info("Decryption successful")
    else:
        logger.info("No match found")
        decrypted_body = "Format invalide. Déchiffrement avorté."
    return jsonify(decrypted_body=decrypted_body)
