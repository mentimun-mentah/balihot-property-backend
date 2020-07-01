from flask_restful import Resource, request
from flask_jwt_extended import jwt_required
from services.models.TypeModel import Type
from services.models.FacilityModel import Facility
from services.models.PropertyModel import Property
from services.models.PropertyPriceModel import PropertyPrice
from services.schemas.properties.PropertySchema import PropertySchema
from services.schemas.properties.AddImagePropertySchema import AddImagePropertySchema
from services.middleware.Admin import admin_required
from services.libs.MagicImage import MagicImage
from marshmallow import ValidationError
from slugify import slugify
from typing import List, Dict, Union

_property_schema = PropertySchema()

class CreateProperty(Resource):
    @staticmethod
    def check_facility(data: List[str]) -> None:
        errors = []
        for index,facility in enumerate(data.split(','),1):
            if not Facility.query.get(int(facility)):
                errors.append(str(index))
        if errors:
            raise ValidationError({'facility':['Facility in order {} not found'.format(','.join(errors))]})

    @staticmethod
    def delete_data_unnecessarily(data: Dict[str,Union[str,int]]) -> None:
        type_property = Type.query.get(data['type_id'])

        if type_property.name.lower() == 'land':
            if 'bathroom' in data: data.pop('bathroom',None)
            if 'bedroom' in data: data.pop('bedroom',None)
            if 'facility' in data: data.pop('facility',None)
            if 'building_size' in data: data.pop('building_size',None)
            if 'period' in data: data.pop('period',None)
            if 'daily_price' in data: data.pop('daily_price',None)
            if 'weekly_price' in data: data.pop('weekly_price',None)
            if 'monthly_price' in data: data.pop('monthly_price',None)
            if 'annually_price' in data: data.pop('annually_price',None)

        if len(data['property_for'].split(',')) == 1:
            if data['property_for'].lower() == 'sale':
                if 'period' in data: data.pop('period',None)
                if 'daily_price' in data: data.pop('daily_price',None)
                if 'weekly_price' in data: data.pop('weekly_price',None)
                if 'monthly_price' in data: data.pop('monthly_price',None)
                if 'annually_price' in data: data.pop('annually_price',None)
            if data['property_for'].lower() == 'rent':
                if 'status' in data: data.pop('status',None)
                if 'freehold_price' in data: data.pop('freehold_price',None)
                if 'leasehold_price' in data: data.pop('leasehold_price',None)
                if 'leasehold_period' in data: data.pop('leasehold_period',None)

        if 'status' in data and len(data['status'].split(',')) == 1:
            if data['status'] == 'free hold':
                if 'leasehold_price' in data:
                    data.pop('leasehold_price',None)
                if 'leasehold_period' in data:
                    data.pop('leasehold_period')
            if data['status'] == 'lease hold':
                if 'freehold_price' in data:
                    data.pop('freehold_price',None)

        if 'period' in data:
            if 'daily' not in [x.strip().lower() for x in data['period'].split(',')]:
                data.pop('daily_price',None)
            if 'weekly' not in [x.strip().lower() for x in data['period'].split(',')]:
                data.pop('weekly_price',None)
            if 'monthly' not in [x.strip().lower() for x in data['period'].split(',')]:
                data.pop('monthly_price',None)
            if 'annually' not in [x.strip().lower() for x in data['period'].split(',')]:
                data.pop('annually_price',None)

    @jwt_required
    @admin_required
    def post(self):
        _image_schema = AddImagePropertySchema()
        files = _image_schema.load(request.files)
        data = _property_schema.load(request.form)
        # delete data unnecessarily before validate
        CreateProperty.delete_data_unnecessarily(data)

        if len(files['images']) < 5:
            raise ValidationError({'images':['Minimum 5 images to be upload']})
        # check name exists in db
        if Property.query.filter_by(name=data['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})

        if 'facility' in data:
            CreateProperty.check_facility(data['facility'])
        # save images
        slug = slugify(data['name'])
        magic_image = MagicImage(file=files['images'],width=1144,height=763,path_upload='properties/',
            square=False,dir_name=slug)
        magic_image.save_image()
        images = ','.join(magic_image.FILE_NAME.values())
        # save data to db
        property_db = Property(**data,slug=slug,images=images)
        property_db.save_to_db()
        # save price to db
        property_price = PropertyPrice(**data,property_id=property_db.id)
        property_price.save_to_db()
        if 'facility' in data:
            # many to many between property and facility
            [property_db.facilities.append(Facility.query.get(int(facility))) for facility in data['facility'].split(',')]
            property_db.save_to_db()
        return {"message":"Success add property."}, 201

class GetUpdateDeleteProperty(Resource):
    @jwt_required
    @admin_required
    def get(self,id: int):
        property_db = Property.query.filter_by(id=id).first_or_404("Property not found")
        return _property_schema.dump(property_db), 200
