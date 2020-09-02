import os
from flask import current_app
from flask_restful import Resource, request
from services.libs.MailSmtp import MailSmtp, MailSmtpException
from services.schemas.email_enquiries.EmailEnquirySchema import EmailEnquirySchema

_email_enquiry_schema = EmailEnquirySchema()

class SendEmailEnquiry(Resource):
    def post(self):
        data = request.get_json()
        args = _email_enquiry_schema.load(data)
        args['phone'] = '0{}'.format(int(args['phone']))

        try:
            MailSmtp.send_email(
                [os.getenv('EMAIL_ENQUIRY')],
                'Email Enquiry',
                'email/EmailEnquiry.html',
                **args
            )
            # subscribe newsletter & property
            with current_app.test_client() as client:
                client.post(
                    '/subscribe',
                    json={'email': args['sender_email'],'subscribe_type':'newsletter','subscribe_from':'login'}
                )
                client.post(
                    '/subscribe',
                    json={'email': args['sender_email'],'subscribe_type':'property','subscribe_from':'login'}
                )
        except MailSmtpException as err:
            return {"error":str(err)}, 500

        return {"message":"Email enquiry has send"}, 200
