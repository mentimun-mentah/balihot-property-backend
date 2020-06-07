from marshmallow import Schema, fields, validate, validates, ValidationError
from re import match

class FacilitySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True,validate=validate.Length(min=3,max=50))
    icon = fields.Str(required=True,validate=validate.Length(min=3,max=40))

    @validates('icon')
    def validate_icon(self,value):
        if not match(r"fa(r|s|l|d|b|) fa-[a-zA-Z0-9-]+",value):
            raise ValidationError('Invalid icon format.')
