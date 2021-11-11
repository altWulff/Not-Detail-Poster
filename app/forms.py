from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, \
    SelectField, FormField, FieldList, DecimalField, RadioField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange, Required, InputRequired
from flask_security import current_user
from app.models import Barista, Shop, Category


class MyFloatField(DecimalField):
    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0].replace(',', '.'))
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid float value'))


class NonValidatingSelectMultipleField(SelectMultipleField):
    def pre_validate(self, form):
        pass 


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
    money = IntegerField(
        'Сумма траты',
        validators=[
            InputRequired(),
            NumberRange(
                min=0,
                message='Сумма не может быть нулевой, либо ниже нуля'
            )
        ]
    )
    is_global = BooleanField('Глобальный?', default=False)
    coffee_shop = SelectField('Кофейня', validators=[DataRequired(message="Выберите кофейню")])
    categories = NonValidatingSelectMultipleField('Категории')

    submit = SubmitField('Отправить') 
    
    def __init__(self, *args, **kwargs):
        super(ExpanseForm, self).__init__(*args, **kwargs)
        self.coffee_shop.choices = [(c.id, c) for c in Shop.get_barista_work(current_user.id).all()]
        self.categories.choices = [(c.id, c) for c in Category.query.all()]


class ByWeightForm(FlaskForm):
    coffee_shop = SelectField('Кофейня')
    by_weight_choice = SelectField('Выбор товара', choices=[
        ('blend', 'Бленд'), ('arabica', 'Арабика')], validators=[Required()], default='blend')
    amount = MyFloatField(
        'Количество',
        default=0.0,
        validators=[
            DataRequired(),
            NumberRange(
                min=0.0001,
                message='Количество не может быть нулевым, либо ниже нуля'
            )
        ]
    )
    money = IntegerField(
        'Сумма', validators=[
            InputRequired(),
            NumberRange(
                min=0,
                message='Сумма не может быть нулевой, либо ниже нуля'
            )
        ])
    cash_type = RadioField('Тип денег', choices=[('cash', 'Наличка'), ('cashless', 'Безнал')],
                           validators=[Required()], default='cash')
    submit = SubmitField('Отправить')
    
    def __init__(self, *args, **kwargs):
        super(ByWeightForm, self).__init__(*args, **kwargs)
        self.coffee_shop.choices = [(c.id, c) for c in Shop.get_barista_work(current_user.id).all()]


class WriteOffForm(FlaskForm):
    coffee_shop = SelectField('Coffee Shop')
    write_off_choice = SelectField('Выбор товара', choices=[
        ('blend', 'Бленд'), ('arabica', 'Арабика'), ('milk', 'Молоко'),
        ('panini', 'Панини'), ('hot_dogs', 'Хот-доги')], validators=[Required()], default='blend')
    amount = MyFloatField(
        'Количество',
        default=0.0,
        validators=[
            DataRequired(),
            NumberRange(
                min=0.0001,
                message='Количество не может быть нулевым, либо ниже нуля'
            )
        ]
    )
    submit = SubmitField('Отправить')
    
    def __init__(self, *args, **kwargs):
        super(WriteOffForm, self).__init__(*args, **kwargs)
        self.coffee_shop.choices = [(c.id, c) for c in Shop.get_barista_work(current_user.id).all()]


class SupplyForm(FlaskForm):
    coffee_shop = SelectField('Coffee Shop')
    supply_choice = SelectField('Выбор товара', choices=[
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
    
    def __init__(self, *args, **kwargs):
        super(SupplyForm, self).__init__(*args, **kwargs)
        self.coffee_shop.choices = [(c.id, c) for c in Shop.get_barista_work(current_user.id).all()]


class TransferForm(FlaskForm):
    where_choice = SelectField('Откуда')
    from_choice = SelectField('Куда')
    submit = SubmitField('Отправить')


class ReportForm(FlaskForm):
    shop = SelectField('Кофейня')
    cashless = IntegerField(
        'Безнал',
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=0,
                message='Сумма не может быть нулевой, либо ниже нуля'
            )
        ]
    )
    actual_balance = IntegerField(
        'Фактический остаток',
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=0,
                message='Сумма не может быть нулевой, либо ниже нуля'
            )
        ]
    )
    milk = MyFloatField(
        'Остаток молока',
        default=0.0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-0.0001,
                message='Остаток молока должен быть нулевым, либо больше нуля'
            )
        ]
    )
    blend = MyFloatField(
        'Остаток купажа',
        default=0.0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-0.0001,
                message='Остаток купажа должен быть нулевым, либо больше нуля'
            )
        ]
    )
    arabica = MyFloatField(
        'Остаток арабики',
        default=0.0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-0.0001,
                message='Остаток арабики должен быть нулевым, либо больше нуля'
            )
        ]
    )
    panini = IntegerField(
        'Панини',
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-1,
                message='Остаток хот-догов должен быть нулевым, либо больше нуля'
            )
        ]
    )
    hot_dogs = IntegerField(
        'Хот-доги',
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-1,
                message='Остаток хот-догов должен быть нулевым, либо больше нуля'
            )
        ]
    )
    submit = SubmitField('Подтвердить')
    
    def __init__(self, *args, **kwargs):
        super(ReportForm, self).__init__(*args, **kwargs)
        self.shop.choices = [(c.id, c) for c in Shop.get_barista_work(current_user.id).all()]


class CoffeeShopForm(FlaskForm):
    place_name = StringField('Название кофейни', validators=[DataRequired()])
    address = StringField('Адрес', validators=[DataRequired()])
    cash = IntegerField(
        'Наличка',
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-1,
                message='Сумма должна быть нулевой, либо больше нуля'
            )
        ]
    )
    cashless = IntegerField(
        'Безнал',
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-1,
                message='Сумма должна быть нулевой, либо больше нуля'
            )
        ]
    )

    coffee_machine = StringField('Кофе машина', default='')
    grinder_1 = StringField('Кофемолка 1', default='')
    grinder_2 = StringField('Кофемолка 2', default='')

    milk = MyFloatField(
        'Молоко',
        default=0.0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-0.0001,
                message='Количество молока должно быть нулевым, либо больше нуля'
            )
        ]
    )
    blend = MyFloatField(
        'Купаж',
        default=0.0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-0.0001,
                message='Количество бленда должно быть нулевым, либо больше нуля'
            )
        ]
    )
    arabica = MyFloatField(
        'Арабика',
        default=0.0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-0.0001,
                message='Количество арабики должно быть нулевым, либо больше нуля'
            )
        ]
    )
    panini = IntegerField(
        'Панини',
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-1,
                message='Количество панини должно быть нулевым, либо больше нуля'
            )
        ]
    )
    hot_dogs = IntegerField(
        'Хот-доги',
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-1,
                message='Количество хот-догов должно быть нулевым, либо больше нуля'
            )
        ]
    )
    submit = SubmitField('Создать')
