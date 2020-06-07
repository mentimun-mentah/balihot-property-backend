from services.serve import db

class Facility(db.Model):
    __tablename__ = 'facilities'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(50),unique=True,index=True,nullable=False)
    icon = db.Column(db.String(40),unique=True,index=True,nullable=False)

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
