from re import match
from marshmallow import Schema, fields, validate, validates, ValidationError, validates_schema
from services.models.TypeModel import Type
from services.models.RegionModel import Region

# TODO:
# set load_only

class PropertySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    type_id = fields.Int(required=True,validate=validate.Range(min=1,error="Value must be greater than 0"))
    region_id = fields.Int(required=True,validate=validate.Range(min=1,error="Value must be greater than 0"))
    property_for = fields.Str(required=True,validate=validate.Length(min=3,max=9))
    land_size = fields.Int(required=True,validate=validate.Range(min=1,error="Value must be greater than 0"))
    youtube = fields.Str(required=True,validate=validate.Length(min=3,max=100))
    description = fields.Str(required=True,validate=validate.Length(min=3))
    # for property sale
    status = fields.Str(validate=validate.Length(min=3,max=20))
    freehold_price = fields.Int(validate=validate.Range(min=1,error="Value must be greater than 0"))
    leasehold_price = fields.Int(validate=validate.Range(min=1,error="Value must be greater than 0"))
    leasehold_period = fields.Str(validate=validate.Length(min=3,max=40))
    # for property rent
    period = fields.Str(validate=validate.Length(min=3,max=40))
    daily_price = fields.Int(validate=validate.Range(min=1,error="Value must be greater than 0"))
    weekly_price = fields.Int(validate=validate.Range(min=1,error="Value must be greater than 0"))
    monthly_price = fields.Int(validate=validate.Range(min=1,error="Value must be greater than 0"))
    annually_price = fields.Int(validate=validate.Range(min=1,error="Value must be greater than 0"))
    # for villa
    facility = fields.Str(load_only=True,validate=validate.Length(min=1))
    bedroom = fields.Int(validate=validate.Range(min=1,error="Value must be greater than 0"))
    bathroom = fields.Int(validate=validate.Range(min=1,error="Value must be greater than 0"))
    building_size = fields.Int(validate=validate.Range(min=1,error="Value must be greater than 0"))
    # for map
    location = fields.Str(required=True,validate=validate.Length(min=3))
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)

    @validates('type_id')
    def validate_type_id(self,value):
        if not Type.query.get(value):
            raise ValidationError('Type not found')

    @validates('region_id')
    def validate_region_id(self,value):
        if not Region.query.get(value):
            raise ValidationError('Region not found')

    @validates('property_for')
    def validate_property_for(self,value):
        # example valid data: sale,rent
        for check in [x.strip().lower() for x in value.split(',')]:
            if check not in ['sale','rent']:
                raise ValidationError('Property For must be between Sale or Rent')

    @validates('status')
    def validate_status(self,value):
        # example valid data: free hold,lease hold
        for check in [x.lower() for x in value.split(',')]:
            if check not in ['free hold','lease hold']:
                raise ValidationError('Status must be Lease Hold or Free Hold')

    @validates('period')
    def validate_period(self,value):
        # example valid data: annually,monthly,daily,weekly
        compared_data = ['daily','weekly','monthly','annually']
        for check in [x.strip().lower() for x in value.split(',')]:
            if check not in compared_data:
                raise ValidationError('Period must be between {}'.format(', '.join(compared_data)))

    @validates('youtube')
    def validate_youtube(self,value):
        if not match(r"http(?:s?):\/\/(?:www\.)?youtu(?:be\.com\/watch\?v=|\.be\/)([\w\-\_]*)(&(amp;)?[\w\?=]*)?",value):
            raise ValidationError('Invalid youtube format.')

    @validates('facility')
    def validate_facility(self,value):
        # example valid data: 1,2,3,4
        try:
            [int(x) for x in value.split(',')]
        except Exception:
            raise ValidationError('Invalid facility format.')

    @validates_schema
    def validate_data(self,data,**kwargs):
        errors = dict()

        type_property = Type.query.get(data['type_id'])

        # check if property for sale is exists
        for check in [x.strip().lower() for x in data['property_for'].split(',')]:
            if check == 'sale' and 'status' not in data:
                errors['status'] = ['Missing data for required field.']
            if check == 'rent' and 'period' not in data and type_property.name.lower() != 'land':
                errors['period'] = ['Missing data for required field.']

        # validation status
        if 'status' in data:
            for check in [x.lower() for x in data['status'].split(',')]:
                # validation status free hold
                if check == 'free hold' and 'freehold_price' not in data:
                    errors['freehold_price'] = ['Missing data for required field.']
                # validation status lease hold
                if check == 'lease hold':
                    if 'leasehold_price' not in data:
                        errors['leasehold_price'] = ['Missing data for required field.']
                    if 'leasehold_period' not in data:
                        errors['leasehold_period'] = ['Missing data for required field.']

        # validation period price
        if 'period' in data:
            for check in [x.strip().lower() for x in data['period'].split(',')]:
                if check == 'daily' and 'daily_price' not in data:
                    errors['daily_price'] = ['Missing data for required field.']
                if check == 'weekly' and 'weekly_price' not in data:
                    errors['weekly_price'] = ['Missing data for required field.']
                if check == 'monthly' and 'monthly_price' not in data:
                    errors['monthly_price'] = ['Missing data for required field.']
                if check == 'annually' and 'annually_price' not in data:
                    errors['annually_price'] = ['Missing data for required field.']

        # validation for land property
        if type_property.name.lower() == 'land':
            # land cannot multiple status selected
            if 'status' in data and len(data['status'].split(',')) > 1:
                errors['status'] = ['Status cannot multiple select']
                # clear all errors from status free hold and lease hold
                errors.pop('freehold_price',None)
                errors.pop('leasehold_price',None)
                errors.pop('leasehold_period',None)
            # if type is land property for must be sale
            if data['property_for'] != 'sale':
                errors['property_for'] = ['Property For must be sale']

        # validation for villa property
        if type_property.name.lower() == 'villa':
            if 'bedroom' not in data:
                errors['bedroom'] = ['Missing data for required field.']
            if 'bathroom' not in data:
                errors['bathroom'] = ['Missing data for required field.']
            if 'facility' not in data:
                errors['facility'] = ['Missing data for required field.']
            if 'building_size' not in data:
                errors['building_size'] = ['Missing data for required field.']

        if errors: raise ValidationError(errors)
