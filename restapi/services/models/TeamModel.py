from services.serve import db

class Team(db.Model):
    __tablename__ = 'teams'

    id = db.Column(db.Integer,primary_key=True)
    image = db.Column(db.String(100),nullable=False)
    name = db.Column(db.String(100),unique=True,index=True,nullable=False)
    title = db.Column(db.String(100),nullable=False)
    phone = db.Column(db.String(20),nullable=False)

    def __init__(self,**args):
        self.image = args['image']
        self.name = args['name']
        self.title = args['title']
        self.phone = args['phone']

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
