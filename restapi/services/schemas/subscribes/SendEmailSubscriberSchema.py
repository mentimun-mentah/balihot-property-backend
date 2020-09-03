from marshmallow import Schema, fields, validate, validates, ValidationError

class SendEmailSubscriberSchema(Schema):
    subscribe_type = fields.Str(required=True,validate=validate.Length(min=3,max=40))
    subject = fields.Str(required=True,validate=validate.Length(min=3,max=40))
    html = fields.Str(required=True,validate=validate.Length(min=3,max=40))
    content = fields.Dict(required=True,validate=validate.Length(min=1))

    @validates('subscribe_type')
    def validate_subscribe_type(self,value):
        check = [
            'newsletter',
            'property',
            'testing'
        ]

        if value not in check:
            raise ValidationError('Subscribe_type must be between {}'.format(', '.join(check)))

    @validates('html')
    def validate_html(self,value):
        check = [
            'email/EmailNewsletter.html',
            'email/EmailProperty.html'
        ]

        if value not in check:
            raise ValidationError('Template email not found')
