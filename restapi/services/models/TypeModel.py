from services.serve import db

class Type(db.Model):
    __tablename__ = 'types'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True,index=True,nullable=False)
    properties = db.relationship('Property',backref='type',cascade='all,delete-orphan')

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
