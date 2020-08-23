from services.serve import db
from slugify import slugify

class Region(db.Model):
    __tablename__ = 'regions'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True,index=True,nullable=False)
    slug = db.Column(db.Text,unique=True,index=True,nullable=False)
    image = db.Column(db.String(100),nullable=False)
    description = db.Column(db.Text,nullable=False)
    properties = db.relationship('Property',backref='region',cascade='all,delete-orphan')

    def __init__(self,**data):
        self.name = data['name']
        self.slug = slugify(self.name)
        self.image = data['image']
        self.description = data['description']

    def update_data_in_db(self,**data) -> "Region":
        self.name = data['name']
        self.slug = slugify(self.name)
        self.description = data['description']
        if data['image']:
            self.image = data['image']

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
