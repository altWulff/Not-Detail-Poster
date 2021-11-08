from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, \
    SelectField, FormField, FieldList, DecimalField, RadioField, SelectMultipleField
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
    name = StringField('Имя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войдти')


class RegistrationForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    phone_number = IntegerField('Телефон', validators=[DataRequired()])
    email = StringField('Емейл', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повтор пароля', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Добавить')

    def validate_username(self, name):
        user = Barista.query.filter_by(name=name.data).first()
        if user is not None:
            raise ValidationError('Please use a different name.')

    def validate_email(self, email):
        user = Barista.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')


class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    phone_number = IntegerField('Phone Number', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


class ExpanseForm(FlaskForm):
    type_cost = RadioField(
        'Type', choices=[('cash', 'Наличка'), ('cashless', 'Безнал')],
        validators=[Required()],
        default='cash'
    )
    money = IntegerField('Сумма траты', validators=[Required(), NumberRange(min=0)])
    is_global = BooleanField('Глобальный?', default=False)
    coffee_shop = SelectField('Кофейня')
    categories = SelectMultipleField('Категории')

    submit = SubmitField('Отправить') 


class ByWeightForm(FlaskForm):
    coffee_shop = SelectField('Кофейня')
    by_weight_choice = RadioField('Выбор товара', choices=[
        ('blend', 'Бленд'), ('arabica', 'Арабика')], validators=[Required()], default='blend')
    amount = MyFloatField('Количество', default=0.0)
    money = IntegerField('Сумма', validators=[Required(), NumberRange(min=0)])
    cash_type = RadioField('Тип денег', choices=[('cash', 'Наличка'), ('cashless', 'Безнал')],
                           validators=[Required()], default='cash')
    submit = SubmitField('Отправить')


class WriteOffForm(FlaskForm):
    coffee_shop = SelectField('Coffee Shop')
    write_off_choice = RadioField('Выбор товара', choices=[
        ('blend', 'Бленд'), ('arabica', 'Арабика'), ('milk', 'Молоко'),
        ('panini', 'Панини'), ('hot_dogs', 'Хот-доги')], validators=[Required()], default='blend')
    amount = MyFloatField('Количество', default=0.0)
    submit = SubmitField('Отправить')


class SupplyForm(FlaskForm):
    coffee_shop = SelectField('Coffee Shop')
    supply_choice = RadioField('Выбор товара', choices=[
        ('blend', 'Бленд'), ('arabica', 'Арабика'), ('milk', 'Молоко'),
        ('panini', 'Панини'), ('hot_dogs', 'Хот-доги')], validators=[Required()], default='blend')
    amount = MyFloatField('Количество', default=0.0)
    cash_type = RadioField(
        'Тип денег',
        choices=[('cash', 'Наличка'), ('cashless', 'Безнал')],
        validators=[Required()],
        default='cash'
    )
    money = IntegerField('Сумма', validators=[Required(), NumberRange(min=0, message='Сумма должна быть больше нуля')])
    submit = SubmitField('Отправить')


class TransferForm(FlaskForm):
    where_choice = SelectField('Откуда')
    from_choice = SelectField('Куда')
    submit = SubmitField('Отправить')


class ReportForm(FlaskForm):
    shop = SelectField('Кофейня')
    cashless = IntegerField('Безнал', default=0)
    actual_balance = IntegerField('Фактический остаток', default=0)
    milk = MyFloatField('Остаток молока', default=0.0)
    blend = MyFloatField('Остаток купажа', default=0.0)
    arabica = MyFloatField('Остаток арабики', default=0.0)
    panini = IntegerField('Панини', default=0)
    hot_dogs = IntegerField('Хот-доги', default=0)
    submit = SubmitField('Подтвердить')


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
