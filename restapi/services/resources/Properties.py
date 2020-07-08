from flask_restful import Resource, request
from flask_jwt_extended import jwt_required
from services.models.TypeModel import Type
from services.models.VisitModel import Visit
from services.models.FacilityModel import Facility
from services.models.PropertyModel import Property
from services.models.PropertyPriceModel import PropertyPrice
from services.schemas.properties.PropertySchema import PropertySchema
from services.schemas.properties.AddImagePropertySchema import AddImagePropertySchema
from services.schemas.properties.UpdateImagePropertySchema import UpdateImagePropertySchema
from services.schemas.properties.DeleteImagePropertySchema import DeleteImagePropertySchema
from services.middleware.Admin import admin_required
from services.libs.MagicImage import MagicImage
from marshmallow import ValidationError
from slugify import slugify
from typing import List, Dict, Union

_property_schema = PropertySchema()

class ValidateProperty:
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

class CreateProperty(Resource):
    @jwt_required
    @admin_required
    def post(self):
        _image_schema = AddImagePropertySchema()
        files = _image_schema.load(request.files)
        data = _property_schema.load(request.form)
        # delete data unnecessarily before validate
        ValidateProperty.delete_data_unnecessarily(data)

        if len(files['images']) < 5:
            raise ValidationError({'images':['Minimum 5 images to be upload']})
        # check name exists in db
        if Property.query.filter_by(name=data['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})

        if 'facility' in data:
            ValidateProperty.check_facility(data['facility'])
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

    @jwt_required
    @admin_required
    def put(self,id: int):
        property_db = Property.query.filter_by(id=id).first_or_404("Property not found")
        _image_schema = UpdateImagePropertySchema()
        files = _image_schema.load(request.files)
        data = _property_schema.load(request.form)
        # delete data unnecessarily before validate
        ValidateProperty.delete_data_unnecessarily(data)
        # check name exists in db
        if property_db.name != data['name'] and Property.query.filter_by(name=data['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})

        if 'facility' in data:
            ValidateProperty.check_facility(data['facility'])

        slug = slugify(data['name'])
        # change folder name if name in db not same with data
        if property_db.name != data['name']:
            MagicImage.rename_folder(old_name=property_db.slug,new_name=slug,path_update='properties/')

        # clear data in db before update
        property_db.property_for = None
        property_db.period = None
        property_db.status = None
        property_db.bedroom = None
        property_db.bathroom = None
        property_db.building_size = None

        if files:
            # save to storage
            magic_image = MagicImage(file=files['images'],width=1144,height=763,path_upload='properties/',
                    square=False,dir_name=slug)
            magic_image.save_image()
            images = ','.join(magic_image.FILE_NAME.values())
            # save to db
            property_db.update_data_in_db(**data,slug=slug,images=images)
            property_db.save_to_db()
        else:
            property_db.update_data_in_db(**data,slug=slug)
            property_db.save_to_db()

        # clear data in db before update
        property_db.price.freehold_price = None
        property_db.price.leasehold_price = None
        property_db.price.leasehold_period = None
        property_db.price.daily_price = None
        property_db.price.weekly_price = None
        property_db.price.monthly_price = None
        property_db.price.annually_price = None
        # save to db
        property_db.price.update_data_in_db(**data)
        property_db.price.save_to_db()

        # delete all relationship from facilities
        property_db.delete_facilities()
        if 'facility' in data:
            # many to many between property and facility
            [property_db.facilities.append(Facility.query.get(int(facility))) for facility in data['facility'].split(',')]
            property_db.save_to_db()
        # change update time in db
        property_db.change_update_time()
        property_db.save_to_db()
        return {"message":"Success update property."}, 200

    @jwt_required
    @admin_required
    def delete(self,id: int):
        property_db = Property.query.filter_by(id=id).first_or_404("Property not found")
        # delete folder with image from storage
        MagicImage.delete_folder(name_folder=property_db.slug,path_delete='properties/')
        property_db.delete_from_db()
        return {"message":"Success delete property."}, 200

class DeleteImageProperty(Resource):
    @jwt_required
    @admin_required
    def post(self,id: int):
        property_db = Property.query.filter_by(id=id).first_or_404("Property not found")
        _delete_property_schema = DeleteImagePropertySchema()
        data = request.get_json()
        args = _delete_property_schema.load(data)
        # check image still 5
        images = [x.split('/')[-1] for x in args['images']]
        delete_image = property_db.images.split(',')
        [delete_image.remove(x) for x in images]
        if len(delete_image) < 5:
            raise ValidationError({'images':['Minimum 5 images to be upload']})

        # delete image from storage
        [MagicImage.delete_image(file=file,path_delete='properties/{}'.format(property_db.slug)) for file in images]
        # update image to db
        property_db.images = ','.join(delete_image)
        property_db.save_to_db()
        return {"message":"Success delete image."}, 200

class AllProperties(Resource):
    def get(self):
        per_page = request.args.get('per_page',default=10,type=int)
        page = request.args.get('page',default=1,type=int)

        lat = request.args.get('lat',default=None,type=float)
        lng = request.args.get('lng',default=None,type=float)
        radius = request.args.get('radius',default=None,type=int)
        region_id = request.args.get('region_id',default=None,type=int)
        type_id = request.args.get('type_id',default=None,type=int)
        property_for = request.args.get('property_for',default=None,type=str)
        period = request.args.get('period',default=None,type=str)
        status = request.args.get('status',default=None,type=str)
        hotdeal = request.args.get('hotdeal',default=None,type=str)
        bedroom = request.args.get('bedroom',default=None,type=int)
        bathroom = request.args.get('bathroom',default=None,type=int)
        location = request.args.get('location',default=None,type=str)
        facility = request.args.get('facility',default=None,type=str)
        min_price = request.args.get('min_price',default=None,type=int)
        max_price = request.args.get('max_price',default=None,type=int)

        args = {
            'lat':lat,
            'lng':lng,
            'radius':radius,
            'region_id':region_id,
            'type_id':type_id,
            'property_for':property_for,
            'period':period,
            'status':status,
            'hotdeal':hotdeal,
            'bedroom':bedroom,
            'bathroom':bathroom,
            'location':location,
            'facility':facility,
            'min_price':min_price,
            'max_price':max_price
        }

        properties = Property.search_properties(per_page=per_page,page=page,**args)
        data = _property_schema.dump(properties.items,many=True)

        results = dict(
            data = data,
            total = properties.total,
            next_num = properties.next_num,
            prev_num = properties.prev_num,
            page = properties.page,
            iter_pages = [x for x in properties.iter_pages()]
        )

        return results, 200

class GetPropertySlug(Resource):
    def get(self,slug: str):
        property_db = Property.query.filter_by(slug=slug).first_or_404("Property not found")
        # set visit if ip not found
        Visit.set_visit(ip=request.remote_addr,visitable_id=property_db.id,visitable_type='view_property')
        data = _property_schema.dump(property_db)
        data['seen'] = Visit.get_seen_activity(visit_type='view_property',visit_id=property_db.id)

        return data, 200
