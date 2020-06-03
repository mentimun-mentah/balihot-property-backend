from flask_restful import Resource, request
from flask_jwt_extended import jwt_required
from services.schemas.categories.CategorySchema import CategorySchema
from services.models.CategoryModel import Category
from services.middleware.Admin import admin_required
from marshmallow import ValidationError

_category_schema = CategorySchema()

class CreateCategory(Resource):
    @jwt_required
    @admin_required
    def post(self):
        data = request.get_json()
        args = _category_schema.load(data)
        if Category.query.filter_by(name=args['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})
        category = Category(name=args['name'])
        category.save_to_db()
        return {"message":"Success add category."}, 201

class GetUpdateDeleteCategory(Resource):
    @jwt_required
    @admin_required
    def get(self,id: int):
        pass

    @jwt_required
    @admin_required
    def put(self,id: int):
        pass

    @jwt_required
    @admin_required
    def delete(self,id: int):
        pass
