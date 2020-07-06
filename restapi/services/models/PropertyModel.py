from services.serve import db
from datetime import datetime
from sqlalchemy import func, or_

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

    def update_data_in_db(self,**args) -> "Property":
        self.name = args['name']
        self.slug = args['slug']
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
        if 'images' in args:
            self.images = f"{self.images},{args['images']}"
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

    def change_update_time(self) -> "Property":
        self.updated_at = datetime.now()

    @classmethod
    def search_properties(cls,per_page: int, page: int, **args) -> "Property":

        if args['lat'] and args['lng'] and args['radius']:
            stmt = db.session.query(
                cls,(
                    6371 * func.acos(func.cos(func.radians(args['lat'])) *
                        func.cos(func.radians(cls.latitude)) *
                        func.cos(func.radians(cls.longitude) - func.radians(args['lng'])) +
                        func.sin(func.radians(args['lat'])) *
                        func.sin(func.radians(cls.latitude))
                    )
                ).label('distance')
            ).subquery()

            location_alias = db.aliased(cls, stmt)
            properties = db.session.query(location_alias) \
                .filter(stmt.c.distance <= args['radius']).order_by(stmt.c.distance) \
                .paginate(page,per_page,error_out=False)
        else:
            stmt = db.session.query(cls)

            if (region_id := args['region_id']): stmt = stmt.filter(cls.region_id == region_id)
            if (type_id := args['type_id']): stmt = stmt.filter(cls.type_id == type_id)
            if (property_for := args['property_for']):
                filters = [cls.property_for.like(f"%{x}%") for x in property_for.split(',')]
                stmt = stmt.filter(or_(*filters))
            if (period := args['period']):
                filters = [cls.period.like(f"%{x}%") for x in period.split(',')]
                stmt = stmt.filter(or_(*filters))
            if (status := args['status']):
                filters = [cls.status.like(f"%{x}%") for x in status.split(',')]
                stmt = stmt.filter(or_(*filters))
            if (hotdeal := args['hotdeal']):
                if hotdeal == 'true':
                    stmt = stmt.filter(cls.hotdeal.is_(True))
            if (bedroom := args['bedroom']):
                stmt = stmt.filter(cls.bedroom == bedroom)
            if (bathroom := args['bathroom']):
                stmt = stmt.filter(cls.bathroom == bathroom)
            if (location := args['location']):
                stmt = stmt.filter(cls.location.like(f"%{location}%"))

            properties = stmt.paginate(page,per_page,error_out=False)

        return properties

    def delete_facilities(self) -> None:
        self.facilities = []
        db.session.commit()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
