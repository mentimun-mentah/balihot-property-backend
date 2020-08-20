from marshmallow import Schema, fields, validate, validates, ValidationError

class EmailEnquirySchema(Schema):
    name = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    sender_email = fields.Email(required=True,validate=validate.Length(max=100))
    phone = fields.Number(required=True,validate=validate.Range(min=1,error="Value must be greater than 0"))
    description = fields.Str(required=True,validate=validate.Length(min=3))

    @validates('phone')
    def validate_phone(self,value):
        value = str(int(value))
        if len(value) < 3 or len(value) >= 20:
            raise ValidationError("Length must be between 3 and 20.")
