from services.serve import db
from datetime import datetime

PropertyFacility = db.Table('property_facilities',
                    db.Column('id',db.Integer,primary_key=True),
                    db.Column('property_id',db.Integer,db.ForeignKey('properties.id',ondelete='cascade'),nullable=False),
                    db.Column('facility_id',db.Integer,db.ForeignKey('facilities.id',ondelete='cascade'),nullable=False))

class Property(db.Model):
    __tablename__ = 'properties'

    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),unique=True,index=True,nullable=False)
    slug = db.Column(db.Text,nullable=False)
    images = db.Column(db.Text,nullable=False)
    property_for = db.Column(db.String(15),nullable=False)
    period = db.Column(db.String(50),nullable=True)
    status = db.Column(db.String(30),nullable=True)
    youtube = db.Column(db.String(100),nullable=False)
    description = db.Column(db.Text,nullable=False)
    hotdeal = db.Column(db.Boolean,default=False)

    bedroom = db.Column(db.Integer,nullable=True)
    bathroom = db.Column(db.Integer,nullable=True)
    building_size = db.Column(db.Integer,nullable=True)
    land_size = db.Column(db.Integer,nullable=False)

    location = db.Column(db.Text,nullable=False)
    latitude = db.Column(db.Float,nullable=False)
    longitude = db.Column(db.Float,nullable=False)
    created_at = db.Column(db.DateTime,default=datetime.now)
    updated_at = db.Column(db.DateTime,default=datetime.now)

    type_id = db.Column(db.Integer,db.ForeignKey('types.id'),nullable=False)
    region_id = db.Column(db.Integer,db.ForeignKey('regions.id'),nullable=False)
    price = db.relationship('PropertyPrice',backref='property',uselist=False,cascade='all,delete-orphan')
    facilities = db.relationship("Facility",secondary=PropertyFacility,backref=db.backref('properties'))

    def __init__(self,**args):
        self.name = args['name']
        self.slug = args['slug']
        self.images = args['images']
        self.property_for = args['property_for']
        self.youtube = args['youtube']
        self.description = args['description']
        self.hotdeal = args['hotdeal']
        self.land_size = args['land_size']
        self.location = args['location']
        self.latitude = args['latitude']
        self.longitude = args['longitude']
        self.type_id = args['type_id']
        self.region_id = args['region_id']
        if 'status' in args:
            self.status = args['status']
        if 'period' in args:
            self.period = args['period']
        if 'bedroom' in args:
            self.bedroom = args['bedroom']
        if 'bathroom' in args:
            self.bathroom = args['bathroom']
        if 'building_size' in args:
            self.building_size = args['building_size']

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
