from flask_restful import Resource, request
from flask_jwt_extended import jwt_required
from services.models.RegionModel import Region
from services.schemas.regions.RegionSchema import RegionSchema
from services.schemas.regions.UpdateImageRegionSchema import UpdateImageRegionSchema
from services.schemas.regions.AddImageRegionSchema import AddImageRegionSchema
from services.libs.MagicImage import MagicImage
from services.middleware.Admin import admin_required
from marshmallow import ValidationError

_region_schema = RegionSchema()

class CreateRegion(Resource):
    @jwt_required
    @admin_required
    def post(self):
        _image_schema = AddImageRegionSchema()
        file = _image_schema.load(request.files)
        data = _region_schema.load(request.form)
        if Region.query.filter_by(name=data['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})

        magic_image = MagicImage(file=file['image'],width=2000,height=3000,path_upload='regions/',square=False)
        magic_image.save_image()
        region = Region(image=magic_image.FILE_NAME,name=data['name'])
        region.save_to_db()
        return {"message":"Success add region."}, 201

class GetUpdateDeleteRegion(Resource):
    @jwt_required
    @admin_required
    def get(self,id: int):
        region = Region.query.filter_by(id=id).first_or_404('Region not found')
        return _region_schema.dump(region), 200

    @jwt_required
    @admin_required
    def put(self,id: int):
        region = Region.query.filter_by(id=id).first_or_404('Region not found')
        _image_schema = UpdateImageRegionSchema()
        file = _image_schema.load(request.files)
        data = _region_schema.load(request.form)
        if region.name != data['name'] and Region.query.filter_by(name=data['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})

        if file:
            MagicImage.delete_image(file=region.image,path_delete='regions/')
            # save image
            magic_image = MagicImage(file=file['image'],width=2000,height=3000,path_upload='regions/',square=False)
            magic_image.save_image()
            region.image = magic_image.FILE_NAME

        region.name = data['name']
        region.save_to_db()
        return {"message":"Success update region."}, 200

    @jwt_required
    @admin_required
    def delete(self,id: int):
        region = Region.query.filter_by(id=id).first_or_404('Region not found')
        MagicImage.delete_image(file=region.image,path_delete='regions/')
        region.delete_from_db()
        return {"message":"Success delete region."}, 200

class AllRegion(Resource):
    def get(self):
        regions = Region.query.all()
        return _region_schema.dump(regions,many=True), 200
