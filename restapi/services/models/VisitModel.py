from services.serve import db
from typing import Dict, Tuple, List
from sqlalchemy import func, desc

class Visit(db.Model):
    __tablename__ = 'visits'

    id = db.Column(db.Integer,primary_key=True)
    ip = db.Column(db.String(20),nullable=False)
    visitable_id = db.Column(db.Integer,nullable=False)
    visitable_type = db.Column(db.String(30),nullable=False)
    created_at = db.Column(db.DateTime,default=func.now())

    def __init__(self,ip: str, visitable_id: int, visitable_type: str):
        self.ip = ip
        self.visitable_id = visitable_id
        self.visitable_type = visitable_type

    @classmethod
    def set_visit(cls,ip: str, visitable_id: int, visitable_type: str) -> None:
        visit = cls.query.filter(cls.ip == ip,
            cls.visitable_id == visitable_id,
            cls.visitable_type == visitable_type).first()
        if not visit:
            save_visit = Visit(ip,visitable_id,visitable_type)
            save_visit.save_to_db()

    @classmethod
    def get_seen_activity(cls,visit_type: str,visit_id: int) -> int:
        return db.session.query(func.count(cls.id)) \
            .filter(cls.visitable_id == visit_id, cls.visitable_type == visit_type) \
            .scalar()

    @classmethod
    def total_visitors(cls,year: int) -> Dict[str,int]:
        import datetime, calendar

        year = year or datetime.datetime.now().year

        visitors = dict()

        for month in range(1,13):
            num_days = calendar.monthrange(year, month)[1]
            start_date = datetime.date(year, month, 1)
            end_date = datetime.date(year, month, num_days)
            visitors[calendar.month_name[month]] = db.session.query(func.count(cls.id)) \
                .filter(cls.created_at >= start_date, cls.created_at <= end_date) \
                .scalar()

        return visitors

    @classmethod
    def visit_popular_by(cls,visit_type: str, limit: int) -> List[Tuple[int,int]]:
        return db.session.query(cls.visitable_id.label('visit_id'),func.count(cls.visitable_id).label('count_total')) \
            .group_by('visit_id') \
            .order_by(desc('count_total')) \
            .filter(cls.visitable_type == visit_type).limit(limit).all()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
