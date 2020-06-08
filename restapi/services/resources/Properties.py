from flask_restful import Resource, request
from flask_jwt_extended import jwt_required
from services.schemas.properties.PropertySchema import PropertySchema
from services.schemas.properties.AddImagePropertySchema import AddImagePropertySchema
from services.middleware.Admin import admin_required
from services.libs.MagicImage import MagicImage

_property_schema = PropertySchema()

class CreateProperty(Resource):
    @jwt_required
    @admin_required
    def post(self):
        from slugify import slugify

        _image_schema = AddImagePropertySchema()
        files = _image_schema.load(request.files)
        data = _property_schema.load(request.form)
        magic_image = MagicImage(file=files['images'],width=1144,height=763,path_upload='properties/',
            square=False,dir_name=slugify(data['name']))
        magic_image.save_image()
        print(magic_image.FILE_NAME)
