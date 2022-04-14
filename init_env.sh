export FLASK_APP=not_detail_poster.py
export FLASK_ENV=development
export SECRET_KEY='super_strong_key'
export DATABASE_URL="postgresql:///dev_db"
createdb dev_db
flask db upgrade
flask translate compile
flask create roles
flask create superuser admin admin
