import os
from flask import current_app
from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from services.models.NewsletterModel import Newsletter
from services.models.VisitModel import Visit
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

        slug = slugify(data['title'],lowercase=False)
        image = MagicImage(file=file['image'],width=3003,height=1287,path_upload='newsletters/',
            dir_name=slug,square=False)
        image.save_image()

        thumbnail = MagicImage(file=file['image'],width=1024,height=686,path_upload='newsletters/',
            dir_name=slug,square=False)
        thumbnail.save_image()

        newsletter = Newsletter(slug=slug,image=image.FILE_NAME,thumbnail=thumbnail.FILE_NAME,**data)
        newsletter.save_to_db()
        # send email notification to subscriber
        access_token = create_access_token(identity=get_jwt_identity())
        title_email = newsletter.title[:25] + '...' if len(newsletter.title) > 25 else newsletter.title
        with current_app.test_client() as client:
            client.post(
                '/send-email/subscriber',
                headers={'Authorization':f"Bearer {access_token}"},
                json={
                    'subscribe_type':'newsletter',
                    'subject': f"Newsletter: {title_email}",
                    'html':'email/EmailNewsletter.html',
                    'content': {
                        'image': f"{os.getenv('BACKEND_URL')}/static/newsletters/{newsletter.slug}/{newsletter.thumbnail}",
                        'link': f"{os.getenv('APP_URL')}/news/{newsletter.slug}",
                        'title': newsletter.title,
                        'description': newsletter.description,
                        'created_at': newsletter.created_at.strftime("%d %B %Y")
                    }
                }
            )

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

        slug = slugify(data['title'],lowercase=False)
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

class AllNewsletters(Resource):
    def get(self):
        per_page = request.args.get('per_page',default=10,type=int)
        page = request.args.get('page',default=1,type=int)

        order_by = request.args.get('order_by',default='desc',type=str)
        q = request.args.get('q',default=None,type=str)

        args = {
            'q': q,
            'order_by': order_by,
        }

        newsletters = Newsletter.search_newsletters(per_page=per_page,page=page,**args)
        data = _newsletter_schema.dump(newsletters.items,many=True)

        results = dict(
            data = data,
            next_num = newsletters.next_num,
            prev_num = newsletters.prev_num,
            page = newsletters.page,
            iter_pages = [x for x in newsletters.iter_pages()]
        )

        return results, 200

class GetNewsletterSlug(Resource):
    def get(self,slug: str):
        newsletter = Newsletter.query.filter_by(slug=slug).first_or_404("Newsletter not found")
        # set visit if ip not found
        Visit.set_visit(ip=request.remote_addr,visitable_id=newsletter.id,visitable_type='view_newsletter')
        data = _newsletter_schema.dump(newsletter)
        data['seen'] = Visit.get_seen_activity(visit_type='view_newsletter',visit_id=newsletter.id)

        return data, 200

class GetNewsletterMostPopular(Resource):
    def get(self):
        limit = request.args.get('limit',default=3,type=int)

        data = list()
        for value in Visit.visit_popular_by(visit_type='view_newsletter',limit=limit):
            index, visitor = value
            try:
                newsletter = Newsletter.query.get(index)
                result = {
                    'id': newsletter.id,
                    'title': newsletter.title,
                    'slug': newsletter.slug,
                    'thumbnail': newsletter.thumbnail,
                    'created_at': str(newsletter.created_at),
                    'updated_at': str(newsletter.updated_at)
                }
                data.append(result)
            except Exception:
                delete_data = Visit.query.filter_by(visitable_id=index).all()
                [x.delete_from_db() for x in delete_data]

        return data, 200

class SearchNewsletterByTitle(Resource):
    def get(self):
        _newsletter_title_schema = NewsletterSchema(only=("title",))
        q = request.args.get('q',default=None,type=str)

        if q: newsletters = Newsletter.search_by_title(q=q)
        else: newsletters = []

        data = _newsletter_title_schema.dump(newsletters,many=True)
        return data, 200
