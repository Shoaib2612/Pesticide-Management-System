from ast import For
from flask_wtf import Form  
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField, SelectField ,PasswordField 
from wtforms import validators, ValidationError 

class loginform(Form):
    name = TextField("User Name ",[validators.Required("Please enter your name.")])  
    password= PasswordField("User Password ",[validators.Required("Please enter your Password.")])
    submit = SubmitField("Submit")  