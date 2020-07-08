from services.serve import db
from datetime import datetime
from sqlalchemy import func

class Visit(db.Model):
    __tablename__ = 'visits'

    id = db.Column(db.Integer,primary_key=True)
    ip = db.Column(db.String(20),nullable=False)
    visitable_id = db.Column(db.Integer,nullable=False)
    visitable_type = db.Column(db.String(30),nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now)

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

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
