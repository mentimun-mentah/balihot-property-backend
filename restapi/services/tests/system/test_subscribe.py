import json
from basetest import BaseTest
from services.models.UserModel import User
from services.models.SubscribeModel import Subscribe

class SubscribeTest(BaseTest):
    def test_00_add_2_user(self):
        self.register(self.EMAIL_TEST,'asd')
        self.register(self.EMAIL_TEST_2,'asd2')

        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST).first())
        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST_2).first())

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

    def test_03_validation_send_email_subscriber(self):
        self.login(self.EMAIL_TEST_2)
        # can't access without role admin
        with self.app() as client:
            res = client.post('/send-email/subscriber',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.role = 2
        user.save_to_db()
        # login user 1
        self.login(self.EMAIL_TEST)

        # subscribe_type, subject, html, content blank
        with self.app() as client:
            res = client.post('/send-email/subscriber',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                json={'subscribe_type':'','subject':'','html':'','content':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Length must be between 3 and 40.'],json.loads(res.data)['subscribe_type'])
            self.assertListEqual(['Length must be between 3 and 40.'],json.loads(res.data)['subject'])
            self.assertListEqual(['Length must be between 3 and 40.'],json.loads(res.data)['html'])
            self.assertListEqual(['Not a valid mapping type.'],json.loads(res.data)['content'])
        # content dict empty
        with self.app() as client:
            res = client.post('/send-email/subscriber',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                json={'content': {}})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Shorter than minimum length 1.'],json.loads(res.data)['content'])
        # valid subscribe_type, html format
        with self.app() as client:
            res = client.post('/send-email/subscriber',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                json={'subscribe_type':'asd','html':'asd'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Subscribe_type must be between newsletter, property, testing'],
                json.loads(res.data)['subscribe_type'])
            self.assertListEqual(['Template email not found'],json.loads(res.data)['html'])

    def test_04_send_email_subscriber(self):
        with self.app() as client:
            res = client.post('/send-email/subscriber',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                json={'subscribe_type':'testing','subject':'Testing','html':'email/EmailNewsletter.html',
                'content':{'asd':'asd'}})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success send email to subscriber.",json.loads(res.data)['message'])

    def test_05_email_already_subscribe(self):
        with self.app() as client:
            res = client.post('/subscribe',
                json={'email': self.EMAIL_TEST,'subscribe_type':'newsletter','subscribe_from':'newsletter'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual([f'{self.EMAIL_TEST} already subscribe newsletter'],json.loads(res.data)['email'])

    def test_06_validation_unsubscribe(self):
        # subscribe not found
        with self.app() as client:
            res = client.delete('/unsubscribe/ngawur')
            self.assertEqual(404,res.status_code)
            self.assertEqual("Subscribe not found",json.loads(res.data)['message'])

    def test_07_unsubscribe(self):
        subscribe = Subscribe.check_email_and_type_exists(self.EMAIL_TEST,'newsletter')
        with self.app() as client:
            res = client.delete('/unsubscribe/{}'.format(subscribe.id))
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success unsubscribe content.",json.loads(res.data)['message'])

    def test_99_delete_user_from_db(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.delete_from_db()
        user = User.query.filter_by(email=self.EMAIL_TEST_2).first()
        user.delete_from_db()
