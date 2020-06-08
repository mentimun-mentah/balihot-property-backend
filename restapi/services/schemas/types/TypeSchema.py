from marshmallow import Schema, fields, validate, validates, ValidationError
from services.models.CategoryModel import Category

class TypeSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    category_id = fields.Int(required=True,strict=True,
        validate=validate.Range(min=1,error="Value must be greater than 0"))

    @validates('category_id')
    def validate_category_id(self,value):
        if not Category.query.get(value):
            raise ValidationError('Category not found')
