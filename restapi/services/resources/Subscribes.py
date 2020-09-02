from flask_restful import Resource, request
from services.models.SubscribeModel import Subscribe
from services.schemas.subscribes.SubscribeSchema import SubscribeSchema

_subscribe_schema = SubscribeSchema()

class SubscribeContent(Resource):
    def post(self):
        data = request.get_json()
        args = _subscribe_schema.load(data)
        subscribe = Subscribe(**args)
        subscribe.save_to_db()
        return {"message":"Success subscribe content."}, 201

class UnsubscribeContent(Resource):
    def delete(self,id: str):
        subscribe = Subscribe.query.filter_by(id=id).first_or_404('Subscribe not found')
        subscribe.delete_from_db()
        return {"message":"Success unsubscribe content."}, 200
