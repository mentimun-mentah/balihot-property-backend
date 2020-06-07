from flask_restful import Resource, request
from flask_jwt_extended import jwt_required
from services.schemas.facilities.FacilitySchema import FacilitySchema
from services.models.FacilityModel import Facility
from services.middleware.Admin import admin_required
from marshmallow import ValidationError

_facility_schema = FacilitySchema()

class CreateFacility(Resource):
    @jwt_required
    @admin_required
    def post(self):
        data = request.get_json()
        args = _facility_schema.load(data)
        if Facility.query.filter_by(name=args['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})

        if Facility.query.filter_by(icon=args['icon']).first():
            raise ValidationError({'icon':['The icon has already been taken.']})

        facility = Facility(name=args['name'],icon=args['icon'])
        facility.save_to_db()
        return {"message":"Success add facility."}, 201

class GetUpdateDeleteFacility(Resource):
    @jwt_required
    @admin_required
    def get(self,id: int):
        facility = Facility.query.filter_by(id=id).first_or_404('Facility not found')
        return _facility_schema.dump(facility), 200

    @jwt_required
    @admin_required
    def put(self,id: int):
        facility = Facility.query.filter_by(id=id).first_or_404('Facility not found')
        data = request.get_json()
        args = _facility_schema.load(data)
        if facility.name != args['name'] and Facility.query.filter_by(name=args['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})

        if facility.icon != args['icon'] and Facility.query.filter_by(icon=args['icon']).first():
            raise ValidationError({'icon':['The icon has already been taken.']})

        facility.name = args['name']
        facility.icon = args['icon']
        facility.save_to_db()
        return {"message":"Success update facility."}, 200

    @jwt_required
    @admin_required
    def delete(self,id: int):
        facility = Facility.query.filter_by(id=id).first_or_404('Facility not found')
        facility.delete_from_db()
        return {"message":"Success delete facility."}, 200

class AllFacility(Resource):
    def get(self):
        facilities = Facility.query.all()
        return _facility_schema.dump(facilities,many=True), 200
