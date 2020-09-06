from services.serve import db, bcrypt
from typing import List, Tuple
from sqlalchemy import func, desc, or_

Wishlist = db.Table('wishlists',
           db.Column('id',db.Integer,primary_key=True),
           db.Column('property_id',db.Integer,db.ForeignKey('properties.id',ondelete='cascade'),nullable=False),
           db.Column('user_id',db.Integer,db.ForeignKey('users.id',ondelete='cascade'),nullable=False))

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(100),unique=True,index=True,nullable=False)
    password = db.Column(db.String(100),nullable=True)
    role = db.Column(db.Integer,default=1)
    avatar = db.Column(db.String(100),default='default.png')
    created_at = db.Column(db.DateTime,default=func.now())
    updated_at = db.Column(db.DateTime,default=func.now())

    confirmation = db.relationship('Confirmation',backref='user',uselist=False,cascade='all,delete-orphan')
    wishlists = db.relationship('Property',secondary=Wishlist,backref=db.backref('user_wishlists'))

    def __init__(self,**args):
        self.username = args['username']
        self.email = args['email']
        if 'avatar' in args:
            self.avatar = args['avatar']
        if 'password' in args:
            self.password = bcrypt.generate_password_hash(args['password']).decode("utf-8")

    @classmethod
    def check_wishlist(cls,property_id: int, user_id: int) -> Wishlist:
        return db.session.query(Wishlist) \
            .filter(Wishlist.c.property_id == property_id, Wishlist.c.user_id == user_id) \
            .first()

    @classmethod
    def loved_properties(cls,limit: int) -> List[Tuple[int,int]]:
        return db.session.query(Wishlist.c.property_id.label('wishlist_id'),
            func.count(Wishlist.c.property_id).label('count_total')) \
            .group_by('wishlist_id') \
            .order_by(desc('count_total')) \
            .limit(limit).all()

    def get_wishlist_property(self,per_page: int, page: int, **args) -> Wishlist:
        from services.models.PropertyModel import Property

        stmt = db.session.query(Wishlist).filter(Wishlist.c.user_id == self.id).join(Property) \
            .order_by(desc(Wishlist.c.id))
        if (type_id := args['type_id']):
            stmt = stmt.filter(Property.type_id == type_id)
        if (status := args['status']):
            filters = [Property.status.like(f"%{x}%") for x in status.split(',')]
            stmt = stmt.filter(or_(*filters))
        if (period := args['period']):
            filters = [Property.period.like(f"%{x}%") for x in period.split(',')]
            stmt = stmt.filter(or_(*filters))

        properties = stmt.paginate(page,per_page,error_out=False)
        return properties

    def delete_wishlist(self,property_id: int) -> None:
        for index,value in enumerate(self.wishlists):
            if value.id == property_id:
                self.wishlists.pop(index)

        db.session.commit()

    def change_update_time(self) -> "User":
        self.updated_at = func.now()

    def check_pass(self,password: str) -> bool:
        return bcrypt.check_password_hash(self.password,password)

    def hash_password(self,password: str) -> "User":
        self.password = bcrypt.generate_password_hash(password).decode("utf-8")

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
