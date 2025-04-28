from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Length

class PromptForm(FlaskForm):
    """Form for solar assistant prompts with validation"""
    prompt = TextAreaField('Enter your solar system design query', 
                         validators=[
                             DataRequired(message="Please enter a prompt."),
                             Length(min=10, max=2000, message="Prompt must be between 10 and 2000 characters.")
                         ])
    language = SelectField('Language', choices=[
        ('en', 'English'),
        ('sw', 'Kiswahili'),
        ('ar', 'Arabic'),
        ('am', 'Amharic'),
        ('es', 'Spanish'),
        ('fr', 'French')
    ], default='en')
    submit = SubmitField('Generate Report')