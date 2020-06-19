from marshmallow import Schema, fields, validate, validates, ValidationError

class TeamSchema(Schema):
    id = fields.Int(dump_only=True)
    image = fields.Str(dump_only=True)
    name = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    title = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    phone = fields.Number(required=True,validate=validate.Range(min=1,error="Value must be greater than 0"))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates('phone')
    def validate_phone(self,value):
        value = str(int(value))
        if len(value) < 3 or len(value) >= 20:
            raise ValidationError("Length must be between 3 and 20.")
