from marshmallow import Schema, fields, validate

class PropertySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    category_id = fields.Int(required=True,validate=validate.Range(min=1,error="Value must be greater than 0"))
