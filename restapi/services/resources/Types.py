from flask_restful import Resource
from services.models.TypeModel import Type
from services.schemas.types.TypeSchema import TypeSchema

_type_schema = TypeSchema()

class AllType(Resource):
    def get(self):
        types = Type.query.all()
        return _type_schema.dump(types,many=True), 200
