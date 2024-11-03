from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length


class EmailForm(FlaskForm):
    recipient = StringField("Destinataire", validators=[DataRequired(), Email()])
    subject = StringField("Objet", validators=[DataRequired(), Length(max=255)])
    body = TextAreaField("", validators=[DataRequired()])
    submit = SubmitField("Envoyer")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Connexion")


class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("S'inscrire")
