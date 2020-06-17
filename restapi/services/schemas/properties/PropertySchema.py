from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from services.models.TypeModel import Type

class PropertySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    facility = fields.Str(load_only=True,required=True,validate=validate.Length(min=1))
    description = fields.Str(required=True,validate=validate.Length(min=3))
    price = fields.Int(required=True,validate=validate.Range(min=1,error="Value must be greater than 0"))
    status = fields.Str(required=True,validate=validate.Length(min=3,max=20))
    period = fields.Str(validate=validate.Length(min=3,max=20))
    property_for = fields.Str(required=True,validate=validate.Length(min=3,max=20))
    type_id = fields.Int(required=True,validate=validate.Range(min=1,error="Value must be greater than 0"))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    @validates('facility')
    def validate_facility(self,value):
        try:
            [int(x) for x in value.split(',')]
        except Exception:
            raise ValidationError('Invalid facility format.')

    @validates('property_for')
    def validate_property_for(self,value):
        if value not in ['For Sale','For Rent']:
            raise ValidationError('Property For must be For Sale or For Rent')

    @validates('type_id')
    def validate_type_id(self,value):
        if not Type.query.get(value):
            raise ValidationError('Type not found')

    @validates_schema
    def validate_period(self,data,**kwargs):
        if data['property_for'] == 'For Rent':
            if data['status'] not in ['Short Term','Long Term']:
                raise ValidationError({'status':['Status must be Short Term or Long Term']})

            if 'period' not in data:
                raise ValidationError({'period':['Missing data for required field.']})

            compared_data = ['Daily','Weekly','Monthly','Annually']
            if data['period'] not in compared_data:
                raise ValidationError({'period':['Period must be between {}'.format(', '.join(compared_data))]})

        if data['property_for'] == 'For Sale':
            if data['status'] not in ['Lease Hold','Free Hold']:
                raise ValidationError({'status':['Status must be Lease Hold or Free Hold']})
