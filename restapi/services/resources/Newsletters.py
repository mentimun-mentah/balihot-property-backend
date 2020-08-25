from flask_restful import Resource, request
from flask_jwt_extended import jwt_required
from services.models.NewsletterModel import Newsletter
from services.schemas.newsletters.NewsletterSchema import NewsletterSchema
from services.schemas.newsletters.AddImageNewsletterSchema import AddImageNewsletterSchema
from services.middleware.Admin import admin_required
from services.libs.MagicImage import MagicImage
from marshmallow import ValidationError
from slugify import slugify

_newsletter_schema = NewsletterSchema()

class CreateNewsletter(Resource):
    @jwt_required
    @admin_required
    def post(self):
        _image_schema = AddImageNewsletterSchema()
        file = _image_schema.load(request.files)
        data = _newsletter_schema.load(request.form)
        if Newsletter.query.filter_by(title=data['title']).first():
            raise ValidationError({'title':['The title has already been taken.']})

        slug = slugify(data['title'])
        image = MagicImage(file=file['image'],width=3003,height=1287,path_upload='newsletters/',
            dir_name=slug,square=False)
        image.save_image()

        thumbnail = MagicImage(file=file['image'],width=1024,height=686,path_upload='newsletters/',
            dir_name=slug,square=False)
        thumbnail.save_image()
        print(file)
        print(data)

class GetUpdateDeleteNewsletter(Resource):
    @jwt_required
    @admin_required
    def get(self,id: int):
        pass

    @jwt_required
    @admin_required
    def put(self,id: int):
        pass

    @jwt_required
    @admin_required
    def delete(self,id: int):
        pass
