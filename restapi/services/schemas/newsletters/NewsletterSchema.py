from marshmallow import Schema, fields, validate

class NewsletterSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    description = fields.Str(required=True,validate=validate.Length(min=3))
    image = fields.Str(dump_only=True)
    thumbnail = fields.Str(dump_only=True)
    slug = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
