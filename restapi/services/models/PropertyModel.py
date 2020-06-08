from services.serve import db

class Property(db.Model):
    __tablename__ = 'properties'

    id = db.Column(db.Integer,primary_key=True)
