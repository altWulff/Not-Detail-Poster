from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, SubmitField
from wtforms.validators import DataRequired


class ReportsFilterForm(FlaskForm):
    start_date = DateField('Начальная дата', format='%d.%m.%Y')
    end_date = DateField('Конечная дата', format='%d.%m.%Y')
    target_coffee_shop = SelectField('Кофейня')
    target_barista = SelectField('Бариста')
    submit = SubmitField('Применить')
