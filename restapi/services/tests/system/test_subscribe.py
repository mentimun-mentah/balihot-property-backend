import json
from basetest import BaseTest
from services.models.SubscribeModel import Subscribe

class SubscribeTest(BaseTest):
    def test_00_delete_subscribe_from_login_user(self):
        subscribes = Subscribe.query.filter_by(email=self.EMAIL_TEST).all()
        [subscribe.delete_from_db() for subscribe in subscribes]

    def test_01_validation_subscribe(self):
        # email, subscribe_type, subscribe_from blank
        with self.app() as client:
            res = client.post('/subscribe',json={'email':'','subscribe_type':'','subscribe_from':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Not a valid email address.'],json.loads(res.data)['email'])
            self.assertListEqual(['Length must be between 3 and 40.'],json.loads(res.data)['subscribe_type'])
            self.assertListEqual(['Length must be between 3 and 40.'],json.loads(res.data)['subscribe_from'])
        # valid email
        with self.app() as client:
            res = client.post('/subscribe',json={'email':'asdsd@asd'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Not a valid email address.'],json.loads(res.data)['email'])
        # valid subscribe_type, subscribe_from format
        with self.app() as client:
            res = client.post('/subscribe',json={'subscribe_type':'asd','subscribe_from':'asd'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Subscribe_type must be between newsletter, property'],
                json.loads(res.data)['subscribe_type'])
            self.assertListEqual(['Subscribe_from must be between login, newsletter, enquiry'],
                json.loads(res.data)['subscribe_from'])

    def test_02_subscribe(self):
        with self.app() as client:
            res = client.post('/subscribe',
                json={'email': self.EMAIL_TEST,'subscribe_type':'newsletter','subscribe_from':'newsletter'})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success subscribe content.",json.loads(res.data)['message'])

    def test_03_email_already_subscribe(self):
        with self.app() as client:
            res = client.post('/subscribe',
                json={'email': self.EMAIL_TEST,'subscribe_type':'newsletter','subscribe_from':'newsletter'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual([f'{self.EMAIL_TEST} already subscribe newsletter'],json.loads(res.data)['email'])

    def test_04_validation_unsubscribe(self):
        # subscribe not found
        with self.app() as client:
            res = client.delete('/unsubscribe/ngawur')
            self.assertEqual(404,res.status_code)
            self.assertEqual("Subscribe not found",json.loads(res.data)['message'])

    def test_05_unsubscribe(self):
        subscribe = Subscribe.check_email_and_type_exists(self.EMAIL_TEST,'newsletter')
        with self.app() as client:
            res = client.delete('/unsubscribe/{}'.format(subscribe.id))
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success unsubscribe content.",json.loads(res.data)['message'])
