# Not-Detail-Poster MVP

Упрощённая система автоматизации, аналитики, и отчётов для кофейни.

# Возможности
- ограничение на вход
- ведение отчетов за день
- различные транзакции: расход денежных сумм, поступление товара, перемещение товара, и его списание
- различные роли пользователей: администратор, модератор, пользователь (сотрудник/бариста).
- админ-панель сайта: администратора (создание, редактирование, удаление), для модератора только редактирование
- базовый перевод, в зависимости от настроек броузера

## Вход и выход из в системы
При входе пользователь видит окно аутентификации, с полями
`Имя` и `Пароль`, у пользователя без имени и пароль нет возможности войди на сайт.
После входа пользователь направляется на главную страницу с отображением карточек кофейных точек.
Для выхода клик на `Выход` во всплывающем меню.

## Отображение кофеен
Отображаются в списке.
В карточке отображается название, адрес, сумма налички и безнал.
Отображаются сотрудники работающие в кофейне. При клике на имя перенаправление на описание профиля сотрудника.
В разворачивающимися полях
- описание оборудования на точке
- остатки на складе
- текущие транзакции кофейни

## Отчеты
По клику на ссылку `Отчеты` пользователь перенаправляется на список отчетов по дням с постраничной пагинацией.
Разное отобрание в зависимости от роли пользователя, для бариста три последних, для модератора, и админа все отчеты.

В отчете отображается название кофейни, кто отправил отчет, дата в формате dd.mm.YYYY
Отчет разделен на три колонки
- в первой: касса, расход за день, остаток дня, безнал, остаток наличности, фактический остаток дня (наличка)
- во второй: глобальные расходы за день, поступления от поставщиков, перемещения товаров
- в третьей: расход товаров за день, и их остаток на конец смены


## Транзакции
При создании транзакции пользователь может выбрать кофейню из списка на которых он работает, для админа ограничений нет.
Все транзакции реализованы через модальное окно. Про успешную валидации, сигнализирует флеш сообщение.

#### Расход
Есть чек бокс глобального расхода, вариант оплаты, категорию(ии) расхода, и его сумма

#### Поступление
При поступлении выбор пришедшего товара, количество, вариант оплаты, сумма.

### Продажа развеса и списание товара
Продажа и списание реализованы аналогично, списание без суммы расхода.

### Закрытие смены
По окончании смены бариста создает отчет кликом на `Создание отчета`, переправляется в форму,
если бариста не взял зарплату, информационное сообщение сообщит об этом.
В форму вводятся данные про полученные
- Безнал за день (Z-отчет)
- Фактический остаток
- остаток арабики, бленда, молока, панини, булочек, и колбасок.
- присутствуют чек-боксы проведенной чистки кофе машины и кофемолок.

### Всплывающее Меню для Администратора
Может через меню создать кофейню,
и добавить сотрудника,

## Панель Администратора
Вход через всплывающее меню на клик `Администрирование` (доступно для админа и модератора), выход при клике на `Выход` в верхней панели.
Здесь нас встречает обзор на созданные кофейни.
Для админа видны все расходы и поступления, модератор может видеть информацию только из кофеен где он работает/модерирует.

#### Кофейни
Выпадающий список кофеен, оборудования, складов и их создание, редактирование, удаление.

#### Статистика
Список отчетов, фильтры для выборки, сортировка по дате и их создание, редактирование, удаление.

#### Двидения товаров
Создание, редактирование, удаление записей про - поступления, развес, списания, перемещения товаров.

#### Кассовые средства
Создание, редактирование, удаление записей про - расходы, внесение денежных средств, и инкассации.

#### Сотрудники
Список сотрудников, создание и редактирование их данных.

#### Разное
Создание и редактирование категорий, а также список ролей и раздача прав доступа пользователям.

## Зависимости
`Python 3`, `PosgreSQL`

### Установка
`$ git clone git@github.com:altWulff/Not-Detail-Poster.git`

`$ cd Not-Detail-Poster`

`$ virtualenv venv`

`$ source venv/bin/activate`

`$ pip install -r requirements.txt`

`$ export FLASK_APP=not_detail_poster.py`

`$ export FLASK_ENV=development`

`$ export SECRET_KEY='super_strong_key'`

`$ export DATABASE_URL="postgresql:///dev_db"`

`$ ./start.sh`

Базовый пользователь и пароль `admin`
