from marshmallow import Schema, fields, validate

class RegionSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    description = fields.Str(required=True,validate=validate.Length(min=3))
    image = fields.Str(dump_only=True)
    slug = fields.Str(dump_only=True)
