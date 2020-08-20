from services.serve import db

class Region(db.Model):
    __tablename__ = 'regions'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True,index=True,nullable=False)
    image = db.Column(db.String(100),nullable=False)
    description = db.Column(db.Text,nullable=False)
    properties = db.relationship('Property',backref='region',cascade='all,delete-orphan')

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
