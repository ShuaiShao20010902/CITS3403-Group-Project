from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, FloatField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Optional

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