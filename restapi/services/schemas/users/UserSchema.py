from marshmallow import Schema, fields, validate

# except role
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    email = fields.Email(required=True,validate=validate.Length(max=100))
    password = fields.Str(load_only=True,required=True,validate=validate.Length(min=6,max=100))
    avatar = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
