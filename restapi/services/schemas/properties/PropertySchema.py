from marshmallow import Schema, fields, validate, validates, validates_schema, ValidationError
from services.models.TypeModel import Type
from services.models.RegionModel import Region

class PropertySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    location = fields.Str(required=True,validate=validate.Length(min=3))
    price_per_are = fields.Int(validate=validate.Range(min=1,error="Value must be greater than 0"))
    land_size = fields.Int(required=True,validate=validate.Range(min=1,error="Value must be greater than 0"))
    building_size = fields.Int(validate=validate.Range(min=1,error="Value must be greater than 0"))
    facility = fields.Str(load_only=True,validate=validate.Length(min=1))
    bedroom = fields.Int(validate=validate.Range(min=1,error="Value must be greater than 0"))
    bathroom = fields.Int(validate=validate.Range(min=1,error="Value must be greater than 0"))
    description = fields.Str(required=True,validate=validate.Length(min=3))
    price = fields.Int(required=True,validate=validate.Range(min=1,error="Value must be greater than 0"))
    status = fields.Str(required=True,validate=validate.Length(min=3,max=20))
    period = fields.Str(validate=validate.Length(min=3,max=20))
    property_for = fields.Str(required=True,validate=validate.Length(min=3,max=20))
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    type_id = fields.Int(required=True,validate=validate.Range(min=1,error="Value must be greater than 0"))
    region_id = fields.Int(required=True,validate=validate.Range(min=1,error="Value must be greater than 0"))

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

    @validates('region_id')
    def validate_region_id(self,value):
        if not Region.query.get(value):
            raise ValidationError('Region not found')

    @validates('type_id')
    def validate_type_id(self,value):
        if not Type.query.get(value):
            raise ValidationError('Type not found')

    @validates_schema
    def validate_period(self,data,**kwargs):
        errors = dict()

        if data['property_for'] == 'For Rent':
            if data['status'] not in ['Short Term','Long Term']:
                errors['status'] = ['Status must be Short Term or Long Term']

            if 'period' not in data:
                errors['period'] = ['Missing data for required field.']

            compared_data = ['Daily','Weekly','Monthly','Annually']
            if 'period' in data and data['period'] not in compared_data:
                errors['period'] = ['Period must be between {}'.format(', '.join(compared_data))]

        if data['property_for'] == 'For Sale':
            if data['status'] not in ['Lease Hold','Free Hold']:
                errors['status'] = ['Status must be Lease Hold or Free Hold']

        # type_id 1 is villa representation
        if data['type_id'] == 1:
            if 'bedroom' not in data:
                errors['bedroom'] = ['Missing data for required field.']
            if 'bathroom' not in data:
                errors['bathroom'] = ['Missing data for required field.']
            if 'facility' not in data:
                errors['facility'] = ['Missing data for required field.']
            if 'building_size' not in data:
                errors['building_size'] = ['Missing data for required field.']

        # type_id 2 is land representation
        if data['type_id'] == 2:
            if 'price_per_are' not in data:
                errors['price_per_are'] = ['Missing data for required field.']

        if errors: raise ValidationError(errors)
