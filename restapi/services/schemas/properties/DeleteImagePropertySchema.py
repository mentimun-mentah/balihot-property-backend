from marshmallow import Schema, fields, validate

class DeleteImagePropertySchema(Schema):
    images = fields.List(fields.Url(),required=True,validate=validate.Length(min=1))
