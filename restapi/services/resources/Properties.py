from flask_restful import Resource, request
from flask_jwt_extended import jwt_required
from services.models.FacilityModel import Facility
from services.models.PropertyModel import Property
from services.schemas.properties.PropertySchema import PropertySchema
from services.schemas.properties.AddImagePropertySchema import AddImagePropertySchema
from services.middleware.Admin import admin_required
from services.libs.MagicImage import MagicImage
from marshmallow import ValidationError
from slugify import slugify
from typing import List

_property_schema = PropertySchema()

class CreateProperty(Resource):
    @staticmethod
    def check_facility(data: List[str]) -> None:
        errors = []
        for index,facility in enumerate(data.split(','),1):
            if not Facility.query.get(int(facility)):
                errors.append(str(index))
        if errors:
            raise ValidationError(
                {'facility':['Facility in order {} not found'.format(','.join(errors))]}
            )

    @jwt_required
    @admin_required
    def post(self):
        _image_schema = AddImagePropertySchema()
        files = _image_schema.load(request.files)
        data = _property_schema.load(request.form)
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
        if 'facility' in data:
            # many to many between property and facility
            [property_db.facilities.append(Facility.query.get(int(facility))) for facility in data['facility'].split(',')]
            property_db.save_to_db()
        return {"message":"Success add property."}, 201
