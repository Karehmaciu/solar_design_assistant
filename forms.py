from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length

class PromptForm(FlaskForm):
    """Form for solar assistant prompts with validation"""
    prompt = TextAreaField('Enter your solar system design query', 
                         validators=[
                             DataRequired(message="Please enter a prompt."),
                             Length(min=10, max=2000, message="Prompt must be between 10 and 2000 characters.")
                         ])
    submit = SubmitField('Generate Report')