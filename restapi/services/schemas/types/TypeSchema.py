from marshmallow import Schema, fields

class TypeSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(dump_only=True)
