from services.serve import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True,index=True,nullable=False)

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
