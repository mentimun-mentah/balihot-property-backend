from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from services.models.SubscribeModel import Subscribe

class SubscribeSchema(Schema):
    id = fields.Str(dump_only=True)
    email = fields.Email(required=True,validate=validate.Length(max=100))
    subscribe_type = fields.Str(required=True,validate=validate.Length(min=3,max=40))
    subscribe_from = fields.Str(required=True,validate=validate.Length(min=3,max=40))
    created_at = fields.DateTime(dump_only=True)

    @validates('subscribe_type')
    def validate_subscribe_type(self,value):
        check = [
            'newsletter',
            'property'
        ]

        if value not in check:
            raise ValidationError('Subscribe_type must be between {}'.format(', '.join(check)))

    @validates('subscribe_from')
    def validate_subscribe_from(self,value):
        check = [
            'login',
            'newsletter',
            'enquiry'
        ]

        if value not in check:
            raise ValidationError('Subscribe_from must be between {}'.format(', '.join(check)))

    @validates_schema
    def validate_email_exists_in_db(self, data, **kwargs):
        if Subscribe.check_email_and_type_exists(data['email'],data['subscribe_type']):
            raise ValidationError(
                {'email': ['{} already subscribe {}'.format(data['email'],data['subscribe_type'])]}
            )
