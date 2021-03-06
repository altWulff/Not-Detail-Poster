"""
This module contains all forms,
custom validators and fields
"""


from flask_babelex import _
from flask_babelex import lazy_gettext as _l
from flask_security import current_user
from flask_wtf import FlaskForm
from wtforms import (BooleanField, DecimalField, IntegerField, PasswordField,
                     RadioField, SelectField, SelectMultipleField, StringField,
                     SubmitField)
from wtforms.validators import (DataRequired, Email, EqualTo, InputRequired,
                                Length, NumberRange, Required, ValidationError)

from app.models import Barista, Category, Shop


class MyFloatField(DecimalField):
    """Float fild, replace ',' to '.' by float types"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.data = None

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = float(valuelist[0].replace(",", "."))
            except ValueError as value_error:
                self.data = None
                raise ValueError(
                    self.gettext("Not a valid float value")
                ) from value_error


class NonValidatingSelectMultipleField(SelectMultipleField):
    """Hack to MultipleField"""

    def pre_validate(self, form):
        pass


class ActualBalanceValidator:
    """Validator for actual balance"""

    def __init__(self, target_shop):
        self.target_shop = target_shop
        self.message = _l(
            "Фактический остаток не может быть меньше вчерашнего остатка налички"
        )

    def __call__(self, form, field):
        form_cash = field.data
        shop_id = getattr(form, self.target_shop).data
        shop = Shop.query.filter_by(id=shop_id).first()
        cash = form_cash - shop.cash
        if cash < 0:
            raise ValidationError(self.message)


class LoginForm(FlaskForm):
    """Login form"""

    name = StringField(_l("Имя"), validators=[DataRequired()])
    password = PasswordField(_l("Пароль"), validators=[DataRequired()])
    remember_me = BooleanField(_l("Запомнить меня"))
    submit = SubmitField(_l("Войти"))


class RegistrationForm(FlaskForm):
    """Registration Form"""

    name = StringField(_l("Имя"), validators=[DataRequired()])
    phone_number = IntegerField(_l("Тел."), validators=[DataRequired()])
    email = StringField(_l("Емейл"), validators=[DataRequired(), Email()])
    password = PasswordField(_l("Пароль"), validators=[DataRequired()])
    password2 = PasswordField(
        _l("Повтор пароля"), validators=[DataRequired(), EqualTo("password")]
    )
    work_place = SelectField(
        _l("Место работы"), validators=[DataRequired(message="Выберите место работы")]
    )
    submit = SubmitField(_l("Добавить"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.work_place.choices = [(s.id, s) for s in Shop.query.all()]

    @staticmethod
    def validate_name(name):
        """Validation user name, by uniq"""
        user = Barista.query.filter_by(name=name.data).first()
        if user is not None:
            raise ValidationError(_("Пожалуйста используйте другое имя."))

    @staticmethod
    def validate_email(email):
        """Validation user email address, by uniq"""
        user = Barista.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_("Пожалуйста используйте другой е-мейл адрес."))


class NewPassword(FlaskForm):
    """New password form"""

    password = PasswordField(
        _l("Новый Пароль"), validators=[DataRequired(), Length(min=8)]
    )
    password2 = PasswordField(
        _l("Повторение пароля"),
        validators=[
            DataRequired(),
            EqualTo("password", message=_l("Пароли не совпадают")),
        ],
    )
    submit = SubmitField(_l("Подтвердить"))


class EditProfileForm(FlaskForm):
    """Edit profile form"""

    name = StringField(_l("Имя"), validators=[DataRequired()])
    phone_number = StringField(_l("Тел."), validators=[DataRequired()])
    email = StringField(_l("Емейл"), validators=[DataRequired(), Email()])
    submit = SubmitField(_l("Сохранить"))

    def __init__(
        self, original_name, original_phone_number, original_email, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.original_name = original_name
        self.original_phone_number = original_phone_number
        self.original_email = original_email

    def validate_name(self, name):
        """Validation username on edit form"""
        if name.data != self.original_name:
            user = Barista.query.filter_by(name=self.name.data).first()
            if user is not None:
                raise ValidationError(
                    _("Пожалуйста используйте другое имя, такое имя уже существует.")
                )

    def validate_phone_number(self, phone_number):
        """Validation phone number on edit form"""
        if phone_number.data != self.original_phone_number:
            p_number = Barista.query.filter_by(
                phone_number=self.phone_number.data
            ).first()
            if p_number is not None:
                raise ValidationError(
                    _(
                        "Пожалуйста используйте другой номер телефона, такой номер уже есть."
                    )
                )

    def validate_email(self, email):
        """Validation email on edit form"""
        if email.data != self.original_email:
            user_email = Barista.query.filter_by(email=self.email.data).first()
            if user_email is not None:
                raise ValidationError(
                    _("Пожалуйста используйте другое имя, такое имя уже существует.")
                )


class ExpanseForm(FlaskForm):
    """Expanse form"""

    type_cost = RadioField(
        "Type",
        choices=[("cash", _l("Наличка")), ("cashless", _l("Безнал"))],
        validators=[Required()],
        default="cash",
    )
    money = IntegerField(
        "Сумма траты",
        validators=[
            InputRequired(),
            NumberRange(
                min=0, message=_l("Сумма не может быть нулевой, либо ниже нуля")
            ),
        ],
    )
    is_global = BooleanField(_l("Глобальный?"), default=False)
    coffee_shop = SelectField(
        _l("Кофейня"), validators=[DataRequired(message=_l("Выберите кофейню"))]
    )
    categories = NonValidatingSelectMultipleField(_l("Категории"))
    submit = SubmitField(_l("Отправить"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if current_user.is_anonymous:
            self.coffee_shop.choices = []
        else:
            self.coffee_shop.choices = [
                (c.id, c) for c in Shop.get_barista_work(current_user).all()
            ]
        self.categories.choices = [(c.id, c) for c in Category.query.all()]


class ByWeightForm(FlaskForm):
    """By weight form"""

    coffee_shop = SelectField(_l("Кофейня"))
    by_weight_choice = SelectField(
        _l("Выбор товара"),
        default="coffee_blend",
        validators=[Required()],
        choices=[("coffee_blend", _l("Бленд")), ("coffee_arabika", _l("Арабика"))],
    )
    amount = MyFloatField(
        _l("Количество"),
        default=0.0,
        validators=[
            DataRequired(),
            NumberRange(
                min=0.0001,
                message=_l("Количество не может быть нулевым, либо ниже нуля"),
            ),
        ],
    )
    money = IntegerField(
        _l("Сумма"),
        validators=[
            InputRequired(),
            NumberRange(
                min=0, message=_l("Сумма не может быть нулевой, либо ниже нуля")
            ),
        ],
    )
    type_cost = RadioField(
        _l("Тип денег"),
        default="cash",
        validators=[Required()],
        choices=[("cash", _l("Наличка")), ("cashless", _l("Безнал"))],
    )
    submit = SubmitField(_l("Отправить"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if current_user.is_anonymous:
            self.coffee_shop.choices = []
        else:
            self.coffee_shop.choices = [
                (c.id, c) for c in Shop.get_barista_work(current_user).all()
            ]


class WriteOffForm(FlaskForm):
    """Write off form"""

    coffee_shop = SelectField(_l("Кофейня"))
    write_off_choice = SelectField(
        _l("Выбор товара"),
        default="coffee_blend",
        validators=[Required()],
        choices=[
            ("coffee_blend", _l("Бленд")),
            ("coffee_arabika", _l("Арабика")),
            ("milk", _l("Молоко")),
            ("panini", _l("Панини")),
            ("sausages", _l("Колбаски")),
            ("buns", _l("Булочки")),
        ],
    )
    amount = MyFloatField(
        _l("Количество"),
        default=0.0,
        validators=[
            DataRequired(),
            NumberRange(
                min=0.0001,
                message=_l("Количество не может быть нулевым, либо ниже нуля"),
            ),
        ],
    )
    submit = SubmitField(_l("Отправить"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if current_user.is_anonymous:
            self.coffee_shop.choices = []
        else:
            self.coffee_shop.choices = [
                (c.id, c) for c in Shop.get_barista_work(current_user).all()
            ]


class SupplyForm(FlaskForm):
    """Supply form"""

    coffee_shop = SelectField(_l("Кофейня"))
    supply_choice = SelectField(
        _l("Выбор товара"),
        default="coffee_blend",
        validators=[Required()],
        choices=[
            ("coffee_blend", _l("Бленд")),
            ("coffee_arabika", _l("Арабика")),
            ("milk", _l("Молоко")),
            ("panini", _l("Панини")),
            ("sausages", _l("Колбаски")),
            ("buns", _l("Булочки")),
        ],
    )
    amount = MyFloatField(_l("Количество"), default=0.0)
    type_cost = RadioField(
        _l("Тип денег"),
        default="cash",
        validators=[Required()],
        choices=[("cash", _l("Наличка")), ("cashless", _l("Безнал"))],
    )
    money = IntegerField(
        _l("Сумма"),
        validators=[
            Required(),
            NumberRange(min=0, message=_l("Сумма должна быть больше нуля")),
        ],
    )
    submit = SubmitField(_l("Отправить"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if current_user.is_anonymous:
            self.coffee_shop.choices = []
        else:
            self.coffee_shop.choices = [
                (c.id, c) for c in Shop.get_barista_work(current_user).all()
            ]


class TransferForm(FlaskForm):
    """Transfer form"""

    where_choice = SelectField(_l("Откуда"))
    from_choice = SelectField(_l("Куда"))
    submit = SubmitField(_l("Отправить"))


class ReportForm(FlaskForm):
    """Daily report form"""

    shop = SelectField(_l("Кофейня"))
    cashless = IntegerField(
        _l("Безнал"),
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=0, message=_l("Сумма не может быть нулевой, либо ниже нуля")
            ),
        ],
    )
    actual_balance = IntegerField(
        _l("Фактический остаток"),
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=0, message=_l("Сумма не может быть нулевой, либо ниже нуля")
            ),
            ActualBalanceValidator(target_shop="shop"),
        ],
    )
    coffee_arabika = MyFloatField(
        _l("Остаток арабики"),
        default=0.0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-0.0001,
                message=_l("Остаток арабики должен быть нулевым, либо больше нуля"),
            ),
        ],
    )
    coffee_blend = MyFloatField(
        _l("Остаток купажа"),
        default=0.0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-0.0001,
                message=_l("Остаток купажа должен быть нулевым, либо больше нуля"),
            ),
        ],
    )
    milk = MyFloatField(
        _l("Остаток молока"),
        default=0.0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-0.0001,
                message=_l("Остаток молока должен быть нулевым, либо больше нуля"),
            ),
        ],
    )
    panini = IntegerField(
        _l("Панини"),
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-1,
                message=_l("Остаток панини должен быть нулевым, либо больше нуля"),
            ),
        ],
    )
    sausages = IntegerField(
        _l("Колбаски"),
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-1,
                message=_l("Остаток колбасок должен быть нулевым, либо больше нуля"),
            ),
        ],
    )
    buns = IntegerField(
        _l("Булочки"),
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-1,
                message=_l("Остаток булочек должен быть нулевым, либо больше нуля"),
            ),
        ],
    )
    cleaning_coffee_machine = BooleanField(
        _("Проведена чистка кофе машины "), default=False
    )
    cleaning_grinder = BooleanField(_("Проведена чистка кофемолок"), default=False)
    submit = SubmitField(_l("Подтвердить"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if current_user.is_anonymous:
            self.shop.choices = []
        else:
            self.shop.choices = [
                (c.id, c) for c in Shop.get_barista_work(current_user).all()
            ]


class CoffeeShopForm(FlaskForm):
    """Coffee shop form"""

    place_name = StringField(_l("Название кофейни"), validators=[DataRequired()])
    address = StringField(_l("Адрес"), validators=[DataRequired()])
    cash = IntegerField(
        _l("Наличка"),
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-1, message=_l("Сумма должна быть нулевой, либо больше нуля")
            ),
        ],
    )
    cashless = IntegerField(
        _l("Безнал"),
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-1, message=_l("Сумма должна быть нулевой, либо больше нуля")
            ),
        ],
    )

    coffee_machine = StringField(_l("Кофе машина"), default="")
    grinder_1 = StringField(_l("Кофемолка 1"), default="")
    grinder_2 = StringField(_l("Кофемолка 2"), default="")

    milk = MyFloatField(
        _l("Молоко"),
        default=0.0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-0.0001,
                message=_l("Количество молока должно быть нулевым, либо больше нуля"),
            ),
        ],
    )
    coffee_blend = MyFloatField(
        _l("Купаж"),
        default=0.0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-0.0001,
                message=_l("Количество бленда должно быть нулевым, либо больше нуля"),
            ),
        ],
    )
    coffee_arabika = MyFloatField(
        _l("Арабика"),
        default=0.0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-0.0001,
                message=_l("Количество арабики должно быть нулевым, либо больше нуля"),
            ),
        ],
    )
    panini = IntegerField(
        _l("Панини"),
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-1,
                message=_l("Количество панини должно быть нулевым, либо больше нуля"),
            ),
        ],
    )
    sausages = IntegerField(
        _l("Колбаски"),
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-1,
                message=_l("Количество колбасок должно быть нулевым, либо больше нуля"),
            ),
        ],
    )
    buns = IntegerField(
        _l("Булочки"),
        default=0,
        validators=[
            InputRequired(),
            NumberRange(
                min=-1,
                message=_l("Количество булочек должно быть нулевым, либо больше нуля"),
            ),
        ],
    )
    staff_list = NonValidatingSelectMultipleField(_l("Добавить сотрудников"))
    submit = SubmitField(_l("Создать"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.staff_list.choices = [(s.id, s) for s in Barista.query.all()]
