import json
from basetest import BaseTest

class EmailEnquiryTest(BaseTest):
    def test_00_validation_send_email_enquiry(self):
        # name, sender_email, phone, description blank
        with self.app() as client:
            res = client.post('/send-email-enquiry',
                    json={'name':'','sender_email':'','phone':'','description':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Length must be between 3 and 100.'],json.loads(res.data)['name'])
            self.assertListEqual(['Not a valid email address.'],json.loads(res.data)['sender_email'])
            self.assertListEqual(['Not a valid number.'],json.loads(res.data)['phone'])
            self.assertListEqual(['Shorter than minimum length 3.'],json.loads(res.data)['description'])
        # check valid sender_email
        with self.app() as client:
            res = client.post('/send-email-enquiry',json={'sender_email':'asdsd@asd'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Not a valid email address.'],json.loads(res.data)['sender_email'])
        # check phone negative number
        with self.app() as client:
            res = client.post('/send-email-enquiry',json={'phone':-1})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Value must be greater than 0"],json.loads(res.data)['phone'])
        # invalid phone number
        with self.app() as client:
            res = client.post('/send-email-enquiry',json={'phone':'08786233dwq231'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Not a valid number."],json.loads(res.data)['phone'])
        # length phone number between 3 and 20
        with self.app() as client:
            res = client.post('/send-email-enquiry',json={'phone':'87862536363727263632'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 20."],json.loads(res.data)['phone'])

    def test_01_send_email_enquiry(self):
        with self.app() as client:
            res = client.post('/send-email-enquiry',json={'name': self.EMAIL_TEST,
                'sender_email': self.EMAIL_TEST,'phone':'08787237464','description':'asdasd'})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Email enquiry has send",json.loads(res.data)['message'])
