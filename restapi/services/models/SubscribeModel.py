import uuid
from services.serve import db
from services.libs.MailSmtp import MailSmtp
from sqlalchemy import func

class Subscribe(db.Model):
    __tablename__ = 'subscribes'

    id = db.Column(db.String(100),primary_key=True)
    email = db.Column(db.String(100),nullable=False)
    subscribe_type = db.Column(db.String(40),nullable=False)
    subscribe_from = db.Column(db.String(40),nullable=False)
    created_at = db.Column(db.DateTime,default=func.now())

    def __init__(self,**args):
        self.id = uuid.uuid4().hex
        self.email = args['email']
        self.subscribe_type = args['subscribe_type']
        self.subscribe_from = args['subscribe_from']

    @classmethod
    def check_email_and_type_exists(cls, email: str, subscribe_type: str) -> "Subscribe":
        return cls.query.filter(cls.email == email, cls.subscribe_type == subscribe_type).first()

    @classmethod
    def send_email_to_subscriber(cls,**args) -> None:
        search_email = cls.query.filter(cls.subscribe_type == args['subscribe_type']).all()
        emails = [x.email for x in search_email]
        if args['subscribe_type'] == 'testing':
            emails = ['asd@gmail.com']

        MailSmtp.send_email(emails,args['subject'],args['html'],**args['content'])

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
