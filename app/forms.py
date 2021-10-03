from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField, TextAreaField, \
    SelectField, FormField, FieldList, DecimalField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange, Required
from app.models import Barista


class MyFloatField(DecimalField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0].replace(',', '.'))
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid float value'))


class LoginForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
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


class LocalExpanseForm(FlaskForm):
    category = StringField('Category', validators=[DataRequired()])
    type_cost = RadioField('Type', choices=[('cash','Наличка'),('cashless','Безнал')], validators=[Required()], default='cash')
    money = IntegerField('Money', validators=[Required(), NumberRange(min=0)])

 
class ExpanseForm(LocalExpanseForm):
    coffee_shop = SelectField('Coffee Shop')
    submit = SubmitField('Submit')   


class ByWeightForm(FlaskForm):
    submit = SubmitField('Отправить')


class WriteOffForm(FlaskForm):
    submit = SubmitField('Отправить')


class SupplyForm(FlaskForm):
    submit = SubmitField('Отправить')


class ReportForm(FlaskForm):
    coffee_shop = SelectField('Coffee Shop')
    cashless = IntegerField('Безнал', default=0)
    actual_balance = IntegerField('Фактический остаток', default=0)
    milk = MyFloatField('Остаток молока', default=0.0)
    blend = MyFloatField('Остаток купажа', default=0.0)
    arabica = MyFloatField('Остаток арабики', default=0.0)
    panini = IntegerField('Панини', default=0)
    hot_dogs = IntegerField('Хот-доги', default=0)
    expanses = FieldList(FormField(LocalExpanseForm), min_entries=1, max_entries=5)
    submit = SubmitField('Submit')


class CoffeeShopForm(FlaskForm):
    place_name = StringField('Название кофейни', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    cash = IntegerField('Наличка', default=0)
    cashless = IntegerField('Безнал', default=0)

    coffee_machine = StringField('Кофе машина', default='')
    grinder_1 = StringField('Кофемолка 1', default='')
    grinder_2 = StringField('Кофемолка 2', default='')

    milk = MyFloatField('Молоко', default=0.0)
    blend = MyFloatField('Купаж', default=0.0)
    arabica = MyFloatField('Бленд', default=0.0)
    panini = IntegerField('Панини', default=0)
    hot_dogs = IntegerField('Хот-доги', default=0)
    submit = SubmitField('Создать')
