from flask_wtf import Form
from wtforms import StringField, TextAreaField,SubmitField, validators

class FeedbackForm(Form):
    name = StringField("Name", [validators.DataRequired()])
    email = StringField("Email", [validators.DataRequired(), validators.Email('your@email.com')])
    subject = StringField("Subject", [validators.DataRequired()])
    message = TextAreaField("Message", [validators.DataRequired()])
    submit = SubmitField("Send Feedback")


