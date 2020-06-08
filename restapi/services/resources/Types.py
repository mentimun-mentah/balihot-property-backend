from flask_restful import Resource, request
from flask_jwt_extended import jwt_required
from services.models.TypeModel import Type
from services.schemas.types.TypeSchema import TypeSchema
from services.middleware.Admin import admin_required
from marshmallow import ValidationError

_type_schema = TypeSchema()

class CreateType(Resource):
    @jwt_required
    @admin_required
    def post(self):
        data = request.get_json()
        args = _type_schema.load(data)
        if Type.query.filter_by(name=args['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})

        type_model = Type(name=args['name'],category_id=args['category_id'])
        type_model.save_to_db()
        return {"message":"Success add type."}, 201

class GetUpdateDeleteType(Resource):
    @jwt_required
    @admin_required
    def get(self,id: int):
        type_model = Type.query.filter_by(id=id).first_or_404('Type not found')
        return _type_schema.dump(type_model), 200

    @jwt_required
    @admin_required
    def put(self,id: int):
        type_model = Type.query.filter_by(id=id).first_or_404('Type not found')
        data = request.get_json()
        args = _type_schema.load(data)
        if type_model.name != args['name'] and Type.query.filter_by(name=args['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})

        type_model.name = args['name']
        type_model.category_id = args['category_id']
        type_model.save_to_db()
        return {"message":"Success update type."}, 200

    @jwt_required
    @admin_required
    def delete(self,id: int):
        type_model = Type.query.filter_by(id=id).first_or_404('Type not found')
        type_model.delete_from_db()
        return {"message":"Success delete type."}, 200

class AllType(Resource):
    def get(self):
        types = Type.query.all()
        return _type_schema.dump(types,many=True), 200
