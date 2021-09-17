from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField, TextAreaField, SelectField, FormField, FieldList
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Barista


class MyFloatField(FloatField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0].replace(',', '.'))
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid float value'))

class LoginForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone_number = IntegerField('Phone Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone_number = IntegerField('Phone Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, name):
        user = Barista.query.filter_by(name=name.data).first()
        if user is not None:
            raise ValidationError('Please use a different name.')
            
    def validate_phone_number(self, phone_number):
        user = Barista.query.filter_by(phone_number=phone_number.data).first()
        if user is not None:
            raise ValidationError('Please use a different phone number.')       

    def validate_email(self, email):
        user = Barista.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone_number = IntegerField('Phone Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


class ExpanceForm(FlaskForm):
    category = StringField('Category')
    type_cost = StringField('Type')
    money = IntegerField('Money')

class ReportForm(FlaskForm):
    coffee_shop = SelectField('Coffee Shop')
    cashbox = IntegerField('Cashbox')
    cash_balance = IntegerField('Cash balance')
    cashless = IntegerField('Cashless')
    remainder_of_day = IntegerField('Remainder of day')
    milk = MyFloatField('Milk')
    blend = MyFloatField('Blend')
    arabica = MyFloatField('Arabica')
    expanses = FieldList(FormField(ExpanceForm))
    submit = SubmitField('Submit')

