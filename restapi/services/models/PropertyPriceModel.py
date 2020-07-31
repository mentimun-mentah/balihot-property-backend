from services.serve import db

class PropertyPrice(db.Model):
    __tablename__ = 'property_prices'

    id = db.Column(db.Integer,primary_key=True)
    freehold_price = db.Column(db.BigInteger,nullable=True)
    leasehold_price = db.Column(db.BigInteger,nullable=True)
    leasehold_period = db.Column(db.String(40),nullable=True)
    daily_price = db.Column(db.BigInteger,nullable=True)
    weekly_price = db.Column(db.BigInteger,nullable=True)
    monthly_price = db.Column(db.BigInteger,nullable=True)
    annually_price = db.Column(db.BigInteger,nullable=True)

    property_id = db.Column(db.Integer,db.ForeignKey('properties.id'),nullable=False)

    def __init__(self,**args):
        self.property_id = args['property_id']
        if 'freehold_price' in args:
            self.freehold_price = args['freehold_price']
        if 'leasehold_price' in args:
            self.leasehold_price = args['leasehold_price']
        if 'leasehold_period' in args:
            self.leasehold_period = args['leasehold_period']
        if 'daily_price' in args:
            self.daily_price = args['daily_price']
        if 'weekly_price' in args:
            self.weekly_price = args['weekly_price']
        if 'monthly_price' in args:
            self.monthly_price = args['monthly_price']
        if 'annually_price' in args:
            self.annually_price = args['annually_price']

    def update_data_in_db(self,**args) -> "PropertyPrice":
        if 'freehold_price' in args:
            self.freehold_price = args['freehold_price']
        if 'leasehold_price' in args:
            self.leasehold_price = args['leasehold_price']
        if 'leasehold_period' in args:
            self.leasehold_period = args['leasehold_period']
        if 'daily_price' in args:
            self.daily_price = args['daily_price']
        if 'weekly_price' in args:
            self.weekly_price = args['weekly_price']
        if 'monthly_price' in args:
            self.monthly_price = args['monthly_price']
        if 'annually_price' in args:
            self.annually_price = args['annually_price']

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
