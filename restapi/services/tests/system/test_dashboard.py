import json
from basetest import BaseTest
from services.models.UserModel import User

class DashboardTest(BaseTest):
    def test_00_add_2_user(self):
        self.register(self.EMAIL_TEST,'asd')
        self.register(self.EMAIL_TEST_2,'asd2')

        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST).first())
        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST_2).first())

    def test_01_get_total_visitor(self):
        self.login(self.EMAIL_TEST_2)
        # can't access without role admin
        with self.app() as client:
            res = client.get('/dashboard/total-visitor',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.role = 2
        user.save_to_db()
        # login user 1
        self.login(self.EMAIL_TEST)

        with self.app() as client:
            res = client.get('/dashboard/total-visitor',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertIn('January',json.loads(res.data).keys())
            self.assertIn('February',json.loads(res.data).keys())
            self.assertIn('March',json.loads(res.data).keys())
            self.assertIn('April',json.loads(res.data).keys())
            self.assertIn('May',json.loads(res.data).keys())
            self.assertIn('June',json.loads(res.data).keys())
            self.assertIn('July',json.loads(res.data).keys())
            self.assertIn('August',json.loads(res.data).keys())
            self.assertIn('September',json.loads(res.data).keys())
            self.assertIn('October',json.loads(res.data).keys())
            self.assertIn('November',json.loads(res.data).keys())
            self.assertIn('December',json.loads(res.data).keys())

    def test_02_get_visitor_properties(self):
        self.login(self.EMAIL_TEST_2)
        # can't access without role admin
        with self.app() as client:
            res = client.get('/dashboard/visitor-properties',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        # login user 1
        self.login(self.EMAIL_TEST)

        with self.app() as client:
            res = client.get('/dashboard/visitor-properties',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertTrue(type(json.loads(res.data)) is list)

    def test_03_get_loved_properties(self):
        self.login(self.EMAIL_TEST_2)
        # can't access without role admin
        with self.app() as client:
            res = client.get('/dashboard/loved-properties',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        # login user 1
        self.login(self.EMAIL_TEST)

        with self.app() as client:
            res = client.get('/dashboard/loved-properties',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertTrue(type(json.loads(res.data)) is list)

    def test_99_delete_user_from_db(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.delete_from_db()
        user = User.query.filter_by(email=self.EMAIL_TEST_2).first()
        user.delete_from_db()
