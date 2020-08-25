from flask_restful import Resource, request
from flask_jwt_extended import jwt_required
from services.models.NewsletterModel import Newsletter
from services.schemas.newsletters.NewsletterSchema import NewsletterSchema
from services.schemas.newsletters.AddImageNewsletterSchema import AddImageNewsletterSchema
from services.schemas.newsletters.UpdateImageNewsletterSchema import UpdateImageNewsletterSchema
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

        newsletter = Newsletter(slug=slug,image=image.FILE_NAME,thumbnail=thumbnail.FILE_NAME,**data)
        newsletter.save_to_db()
        return {"message":"Success add newsletter."}, 201

class GetUpdateDeleteNewsletter(Resource):
    @jwt_required
    @admin_required
    def get(self,id: int):
        newsletter = Newsletter.query.filter_by(id=id).first_or_404('Newsletter not found')
        return _newsletter_schema.dump(newsletter), 200

    @jwt_required
    @admin_required
    def put(self,id: int):
        newsletter = Newsletter.query.filter_by(id=id).first_or_404('Newsletter not found')
        _image_schema = UpdateImageNewsletterSchema()
        file = _image_schema.load(request.files)
        data = _newsletter_schema.load(request.form)

        if newsletter.title != data['title'] and Newsletter.query.filter_by(title=data['title']).first():
            raise ValidationError({'title':['The title has already been taken.']})

        slug = slugify(data['title'])
        # change folder name if name in db not same with data
        if newsletter.title != data['title']:
            MagicImage.rename_folder(old_name=newsletter.slug,new_name=slug,path_update='newsletters/')

        image_name = None
        thumbnail_name = None
        if file:
            # delete image and thumbnail
            MagicImage.delete_image(file=newsletter.image,path_delete='newsletters/{}'.format(slug))
            MagicImage.delete_image(file=newsletter.thumbnail,path_delete='newsletters/{}'.format(slug))
            # save image
            image = MagicImage(file=file['image'],width=3003,height=1287,path_upload='newsletters/',
                dir_name=slug,square=False)
            image.save_image()
            image_name = image.FILE_NAME

            thumbnail = MagicImage(file=file['image'],width=1024,height=686,path_upload='newsletters/',
                dir_name=slug,square=False)
            thumbnail.save_image()
            thumbnail_name = thumbnail.FILE_NAME

        newsletter.update_data_in_db(slug=slug,image=image_name,thumbnail=thumbnail_name,**data)
        newsletter.change_update_time()
        newsletter.save_to_db()
        return {"message":"Success update newsletter."}, 200

    @jwt_required
    @admin_required
    def delete(self,id: int):
        newsletter = Newsletter.query.filter_by(id=id).first_or_404('Newsletter not found')
        # delete folder with image from storage
        MagicImage.delete_folder(name_folder=newsletter.slug,path_delete='newsletters/')
        newsletter.delete_from_db()
        return {"message":"Success delete newsletter."}, 200
