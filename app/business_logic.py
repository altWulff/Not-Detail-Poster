from datetime import datetime, date
from sqlalchemy import func
from app.models import Shop, Report

date_today = datetime(datetime.today().year, datetime.today().month, datetime.today().day)


def transaction_count(shop_id: int) -> int:
    reports = Report.query.filter_by(shop_id=shop_id)
    reports_today = reports.filter(func.date(Report.timestamp) == date.today()).all()
    return len(reports_today)