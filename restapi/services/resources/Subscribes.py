from flask_restful import Resource, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.models.UserModel import User
from services.models.SubscribeModel import Subscribe
from services.schemas.subscribes.SubscribeSchema import SubscribeSchema
from services.schemas.subscribes.SendEmailSubscriberSchema import SendEmailSubscriberSchema
from services.libs.MailSmtp import MailSmtpException
from services.middleware.Admin import admin_required

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

class GetSubscribeUser(Resource):
    @jwt_required
    def get(self):
        user = User.query.get(get_jwt_identity())
        subscribe = Subscribe.query.filter_by(email=user.email).all()
        return _subscribe_schema.dump(subscribe,many=True), 200

class SendEmailToSubscriber(Resource):
    @jwt_required
    @admin_required
    def post(self):
        _send_email_subscriber = SendEmailSubscriberSchema()
        data = request.get_json()
        args = _send_email_subscriber.load(data)
        try:
            Subscribe.send_email_to_subscriber(**args)
        except MailSmtpException as err:
            return {"error":str(err)}, 500

        return {"message":"Success send email to subscriber."}, 200
