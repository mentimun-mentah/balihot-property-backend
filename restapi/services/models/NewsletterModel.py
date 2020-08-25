from services.serve import db
from datetime import datetime

class Newsletter(db.Model):
    __tablename__ = 'newsletters'

    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100),unique=True,index=True,nullable=False)
    slug = db.Column(db.Text,unique=True,index=True,nullable=False)
    image = db.Column(db.String(100),nullable=False)
    thumbnail = db.Column(db.String(100),nullable=False)
    description = db.Column(db.Text,nullable=False)

    created_at = db.Column(db.DateTime,default=datetime.now)
    updated_at = db.Column(db.DateTime,default=datetime.now)

    def change_update_time(self) -> "Newsletter":
        self.updated_at = datetime.now()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
