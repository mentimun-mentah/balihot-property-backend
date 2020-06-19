from flask_restful import Resource, request
from flask_jwt_extended import jwt_required
from services.schemas.teams.UpdateImageTeamSchema import UpdateImageTeamSchema
from services.schemas.teams.AddImageTeamSchema import AddImageTeamSchema
from services.schemas.teams.TeamSchema import TeamSchema
from services.models.TeamModel import Team
from services.libs.MagicImage import MagicImage
from services.middleware.Admin import admin_required
from marshmallow import ValidationError

_team_schema = TeamSchema()

class CreateTeam(Resource):
    @jwt_required
    @admin_required
    def post(self):
        _image_schema = AddImageTeamSchema()
        file = _image_schema.load(request.files)
        data = _team_schema.load(request.form)
        if Team.query.filter_by(name=data['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})

        # save image
        magic_image = MagicImage(file=file['image'],width=366,height=457,path_upload='teams/',square=False)
        magic_image.save_image()
        data['phone'] = str(int(data['phone']))
        data['image'] = magic_image.FILE_NAME
        team = Team(**data)
        team.save_to_db()
        return {"message":"Success add team."}, 201

class GetUpdateDeleteTeam(Resource):
    @jwt_required
    @admin_required
    def get(self,id: int):
        team = Team.query.filter_by(id=id).first_or_404('Team not found')
        return _team_schema.dump(team), 200

    @jwt_required
    @admin_required
    def put(self,id: int):
        team = Team.query.filter_by(id=id).first_or_404('Team not found')
        _image_schema = UpdateImageTeamSchema()
        file = _image_schema.load(request.files)
        data = _team_schema.load(request.form)
        if team.name != data['name'] and Team.query.filter_by(name=data['name']).first():
            raise ValidationError({'name':['The name has already been taken.']})

        if file:
            MagicImage.delete_image(file=team.image,path_delete='teams/')
            # save image
            magic_image = MagicImage(file=file['image'],width=366,height=457,path_upload='teams/',square=False)
            magic_image.save_image()
            team.image = magic_image.FILE_NAME

        team.name = data['name']
        team.title = data['title']
        team.phone = str(int(data['phone']))
        team.change_update_time()
        team.save_to_db()
        return {"message":"Success update team."}, 200

    @jwt_required
    @admin_required
    def delete(self,id: int):
        team = Team.query.filter_by(id=id).first_or_404('Team not found')
        MagicImage.delete_image(file=team.image,path_delete='teams/')
        team.delete_from_db()
        return {"message":"Success delete team."}, 200

class AllTeam(Resource):
    def get(self):
        teams = Team.query.all()
        return _team_schema.dump(teams,many=True), 200
