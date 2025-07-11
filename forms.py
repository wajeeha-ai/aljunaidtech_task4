from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    TextAreaField,
    SelectField,
    BooleanField,
    FileField,
    SelectMultipleField,
    DateTimeField
)
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional
from flask_wtf.file import FileAllowed

# -----------------------------
# Registration Form
# -----------------------------
class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password', validators=[
        DataRequired(), EqualTo('password')
    ])
    role = SelectField('Role', choices=[('reader','Reader'), ('author','Author')])
    submit = SubmitField('Register')

# -----------------------------
# Login Form
# -----------------------------
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

# -----------------------------
# Post Form
# -----------------------------
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=2, max=200)])
    content = TextAreaField('Content', validators=[DataRequired()])
    image = FileField('Upload Image', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'])])
    category = SelectField('Category', coerce=int, validators=[Optional()])
    tags = SelectMultipleField('Tags', coerce=int, validators=[Optional()])
    scheduled_publish = DateTimeField('Schedule Publish Time (optional)', format='%Y-%m-%d %H:%M:%S', validators=[Optional()])
    submit = SubmitField('Save Post')

# -----------------------------
# Comment Form
# -----------------------------
class CommentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[Optional(), Email()])
    content = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Post Comment')

# -----------------------------
# Category Form
# -----------------------------
class CategoryForm(FlaskForm):
    name = StringField('Category Name', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Save')

# -----------------------------
# Tag Form
# -----------------------------
class TagForm(FlaskForm):
    name = StringField('Tag Name', validators=[DataRequired(), Length(min=2, max=50)])
    submit = SubmitField('Save')

# -----------------------------
# Profile Update Form
# -----------------------------
class ProfileUpdateForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('New Password', validators=[Optional()])
    confirm = PasswordField('Confirm New Password', validators=[Optional(), EqualTo('password')])
    submit = SubmitField('Update Profile')
