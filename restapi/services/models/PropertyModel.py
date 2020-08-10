import math
from services.serve import db
from datetime import datetime
from sqlalchemy import func, or_, and_, orm
from sqlalchemy.ext.hybrid import hybrid_method

def gc_distance(lat1, lng1, lat2, lng2, math=math):
    ang = math.acos(math.cos(math.radians(lat1)) *
                    math.cos(math.radians(lat2)) *
                    math.cos(math.radians(lng2) -
                             math.radians(lng1)) +
                    math.sin(math.radians(lat1)) *
                    math.sin(math.radians(lat2)))

    return 6371 * ang


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
    def search_by_location(cls,**kwargs) -> "Property":
        if 'type_id' in kwargs:
            return cls.query.filter(cls.type_id == kwargs['type_id'], cls.location.like('%' + kwargs['q'] + '%')) \
                .limit(20).all()
        else:
            return cls.query.filter(cls.location.like('%' + kwargs['q'] + '%')).limit(20).all()

    @classmethod
    def filter_by_slug(cls,slug: str) -> "Property":
        return cls.query.options(orm.joinedload('facilities'),orm.joinedload('price')) \
            .filter_by(slug=slug).first_or_404("Property not found")

    @classmethod
    def load_similar_listing_random(cls,type_id: int) -> "Property":
        return cls.query.options(orm.joinedload('facilities'),orm.joinedload('price')) \
            .filter_by(type_id=type_id) \
            .order_by(func.random()) \
            .limit(5).all()

    @hybrid_method
    def distance(self, lat, lng):
        return gc_distance(lat, lng, self.latitude, self.longitude)

    @distance.expression
    def distance(cls, lat, lng):
        return gc_distance(lat, lng, cls.latitude, cls.longitude, math=func)

    @classmethod
    def search_properties(cls,per_page: int, page: int, **args) -> "Property":
        from services.models.FacilityModel import Facility
        from services.models.PropertyPriceModel import PropertyPrice

        if args['lat'] and args['lng'] and args['radius']:
            stmt = db.session.query(cls,cls.distance(args['lat'],args['lng']).label('distance'))
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
        if (facility := args['facility']):
            stmt = stmt.filter(cls.facilities.any(Facility.id.in_([x for x in facility.split(',')])))
        if (min_price := args['min_price']) and (max_price := args['max_price']):
            stmt = stmt.filter(
                cls.price.has(
                    or_(
                        and_(PropertyPrice.freehold_price >= min_price, PropertyPrice.freehold_price <= max_price),
                        and_(PropertyPrice.leasehold_price >= min_price, PropertyPrice.leasehold_price <= max_price),
                        and_(PropertyPrice.daily_price >= min_price, PropertyPrice.daily_price <= max_price),
                        and_(PropertyPrice.weekly_price >= min_price, PropertyPrice.weekly_price <= max_price),
                        and_(PropertyPrice.monthly_price >= min_price, PropertyPrice.monthly_price <= max_price),
                        and_(PropertyPrice.annually_price >= min_price, PropertyPrice.annually_price <= max_price)
                    )
                )
            )
        if (min_price := args['min_price']) and not args['max_price']:
            stmt = stmt.filter(
                cls.price.has(
                    or_(
                        PropertyPrice.freehold_price >= min_price,
                        PropertyPrice.leasehold_price >= min_price,
                        PropertyPrice.daily_price >= min_price,
                        PropertyPrice.weekly_price >= min_price,
                        PropertyPrice.monthly_price >= min_price,
                        PropertyPrice.annually_price >= min_price
                    )
                )
            )
        if (max_price := args['max_price']) and not args['min_price']:
            stmt = stmt.filter(
                cls.price.has(
                    or_(
                        PropertyPrice.freehold_price <= max_price,
                        PropertyPrice.leasehold_price <= max_price,
                        PropertyPrice.daily_price <= max_price,
                        PropertyPrice.weekly_price <= max_price,
                        PropertyPrice.monthly_price <= max_price,
                        PropertyPrice.annually_price <= max_price
                    )
                )
            )

        if args['lat'] and args['lng'] and args['radius']:
            stmt = stmt.subquery()
            location_alias = db.aliased(cls, stmt)
            stmt_result = db.session.query(location_alias)

            return stmt_result.options(orm.joinedload('facilities'),orm.joinedload('price')) \
                .filter(stmt.c.distance <= args['radius']).order_by(stmt.c.distance) \
                .paginate(page,per_page,error_out=False)
        else:
            return stmt.options(orm.joinedload('facilities'),orm.joinedload('price')) \
                .paginate(page,per_page,error_out=False)

    def delete_facilities(self) -> None:
        self.facilities = []
        db.session.commit()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
