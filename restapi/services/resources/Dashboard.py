from flask_restful import Resource, request
from flask_jwt_extended import jwt_required
from services.models.UserModel import User
from services.models.VisitModel import Visit
from services.models.PropertyModel import Property
from services.middleware.Admin import admin_required

class GetTotalVisitor(Resource):
    @jwt_required
    @admin_required
    def get(self):
        year = request.args.get('year',default=None,type=int)
        return Visit.total_visitors(year=year), 200

class GetVisitorProperties(Resource):
    @jwt_required
    @admin_required
    def get(self):
        limit = request.args.get('limit',default=3,type=int)

        data = list()
        for value in Visit.visit_popular_by(visit_type='view_property',limit=limit):
            index, visitor = value
            try:
                property_db = Property.query.get(index)
                data.append({'name': property_db.name,'slug': property_db.slug, 'visitor': visitor})
            except Exception:
                delete_data = Visit.query.filter_by(visitable_id=index).all()
                [x.delete_from_db() for x in delete_data]

        return data, 200

class GetLovedProperties(Resource):
    @jwt_required
    @admin_required
    def get(self):
        limit = request.args.get('limit',default=3,type=int)

        data = list()
        for value in User.loved_properties(limit=limit):
            index, loved = value
            property_db = Property.query.get(index)
            data.append({'name': property_db.name,'slug': property_db.slug, 'loved': loved})

        return data, 200
