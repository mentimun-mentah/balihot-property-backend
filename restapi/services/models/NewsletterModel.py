from services.serve import db
from sqlalchemy import func

class Newsletter(db.Model):
    __tablename__ = 'newsletters'

    id = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(100),unique=True,index=True,nullable=False)
    slug = db.Column(db.Text,unique=True,index=True,nullable=False)
    image = db.Column(db.String(100),nullable=False)
    thumbnail = db.Column(db.String(100),nullable=False)
    description = db.Column(db.Text,nullable=False)

    created_at = db.Column(db.DateTime,default=func.now())
    updated_at = db.Column(db.DateTime,default=func.now())

    def __init__(self,**data):
        self.title = data['title']
        self.slug = data['slug']
        self.image = data['image']
        self.thumbnail = data['thumbnail']
        self.description = data['description']

    def update_data_in_db(self,**data) -> "Newsletter":
        self.title = data['title']
        self.slug = data['slug']
        self.description = data['description']
        if data['image']:
            self.image = data['image']
        if data['thumbnail']:
            self.thumbnail = data['thumbnail']

    def change_update_time(self) -> "Newsletter":
        self.updated_at = func.now()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
