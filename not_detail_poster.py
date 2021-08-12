from app import app, db
from app.models import Barista, DailyReport


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Barista': Barista, 'DailyReport': DailyReport}
