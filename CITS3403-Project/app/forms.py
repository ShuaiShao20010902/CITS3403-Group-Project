from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, FloatField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Regexp, NumberRange, Optional
from app.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                        validators=[
                            DataRequired(message="Username is required."),
                            Length(min=3, max=20, message="Username must be between 3 and 20 characters.")
                        ])

    email = StringField('Email',
                        validators=[
                            DataRequired(message="Email is required."),
                            Email(message="Please enter a valid email address.")
                        ])

    password = PasswordField('Password',
                            validators=[
                                DataRequired(message="Password is required."),
                                Length(min=8, message="Password must be at least 8 characters."),
                                Regexp(
                                    '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
                                    message='Password must include at least one lowercase letter, one uppercase letter, one number, and one special character.'
                                )
                            ])

    confirm_password = PasswordField('Confirm Password',
                                    validators=[
                                        DataRequired(message="Please confirm your password."),
                                        EqualTo('password', message="Passwords must match.")
                                    ])

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is already taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please use a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[
                            DataRequired(message="Email is required."),
                            Email(message="Please enter a valid email address.")
                        ])

    password = PasswordField('Password',
                            validators=[
                                DataRequired(message="Password is required.")
                            ])

    remember = BooleanField('Remember Me')

    submit = SubmitField('Log In')


class PasswordResetRequestForm(FlaskForm):
    email = StringField('Email',
                        validators=[
                            DataRequired(message="Email is required."),
                            Email(message="Please enter a valid email address.")
                        ])

    submit = SubmitField('Send Reset Link')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('There is no account with that email. You must register first.')

class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(message="Password is required."),
        Length(min=8, message="Password must be at least 8 characters."),
        Regexp(
            '^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$',
            message='Password must include at least one lowercase letter, one uppercase letter, one number, and one special character.'
        )
    ])

    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password."),
        EqualTo('password', message="Passwords must match.")
    ])

    submit = SubmitField('Reset Password')


class ManualBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()], render_kw={"placeholder": "Enter title, e.g. The Hobbit"})
    author = StringField('Author', validators=[DataRequired()], render_kw={"placeholder": "Enter author, e.g. J. R. R. Tolkien"})
    genres = StringField('Genres', render_kw={"placeholder": "Optional, e.g. Fantasy, Adventure"})
    description = TextAreaField('Description', render_kw={"placeholder": "Optional, Short synopsis…"})
    number_of_pages = IntegerField('Number of Pages', validators=[DataRequired(), NumberRange(min=1)], render_kw={"placeholder": "Enter page numbers, e.g. 310"})
    submit = SubmitField('Import Book')


class CombinedBookForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()], render_kw={"placeholder": "Enter title, e.g. The Hobbit"})
    author = StringField('Author', validators=[DataRequired()], render_kw={"placeholder": "Enter author, e.g. J. R. R. Tolkien"})
    genres = StringField('Genres', render_kw={"placeholder": "Optional, e.g. Fantasy, Adventure"})
    description = TextAreaField('Description', render_kw={"placeholder": "Optional, Short synopsis…"})
    number_of_pages = IntegerField('Number of Pages', validators=[DataRequired(), NumberRange(min=1)], render_kw={"placeholder": "Enter page numbers, e.g. 310"})
    rating = FloatField('Rating (out of 5)', validators=[Optional(), NumberRange(min=0.0, max=5.0)], render_kw={"placeholder": "Enter rating 1 out of 5, e.g. 3"})
    notes = TextAreaField('Notes', validators=[Optional()], render_kw={"placeholder": "Enter user notes, e.g. This book was amazing!"})
    completed = BooleanField('Mark as Completed')
    submit = SubmitField('Import Book')