from marshmallow import Schema, fields, validate

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True,validate=validate.Length(min=3,max=100))
