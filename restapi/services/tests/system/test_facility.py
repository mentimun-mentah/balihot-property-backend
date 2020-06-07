import json
from basetest import BaseTest
from services.models.UserModel import User
from services.models.FacilityModel import Facility

class FacilityTest(BaseTest):
    def test_00_add_2_user(self):
        self.register(self.EMAIL_TEST,'asd')
        self.register(self.EMAIL_TEST_2,'asd2')

        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST).first())
        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST_2).first())

    def test_01_validation_create_facility(self):
        self.login(self.EMAIL_TEST_2)
        # can't access without role admin
        with self.app() as client:
            res = client.post('/facility/create',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.role = 2
        user.save_to_db()
        # login user 1
        self.login(self.EMAIL_TEST)

        # name, icon blank
        with self.app() as client:
            res = client.post('/facility/create',json={'name':'','icon':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 50."],json.loads(res.data)['name'])
            self.assertListEqual(["Length must be between 3 and 40."],json.loads(res.data)['icon'])
        # invalid icon format
        with self.app() as client:
            res = client.post('/facility/create',json={'icon':'faw fa-as'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Invalid icon format."],json.loads(res.data)['icon'])

    def test_02_create_facility(self):
        with self.app() as client:
            res = client.post('/facility/create',json={'name':self.NAME,'icon':'fa fa-test'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add facility.",json.loads(res.data)['message'])

    def test_03_name_icon_already_taken_create_facility(self):
        # name already taken
        with self.app() as client:
            res = client.post('/facility/create',json={'name':self.NAME,'icon':'fa fa-test'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["The name has already been taken."],json.loads(res.data)['name'])

        # icon already taken
        with self.app() as client:
            res = client.post('/facility/create',json={'name':self.NAME_2,'icon':'fa fa-test'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["The icon has already been taken."],json.loads(res.data)['icon'])

    def test_04_get_facility_by_id(self):
        # check user is admin
        self.login(self.EMAIL_TEST_2)

        with self.app() as client:
            res = client.get('/facility/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # facility not found
        with self.app() as client:
            res = client.get('/facility/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Facility not found",json.loads(res.data)['message'])

        # get specific facility
        facility = Facility.query.filter_by(name=self.NAME).first()
        with self.app() as client:
            res = client.get('/facility/crud/{}'.format(facility.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertIn("id",json.loads(res.data).keys())
            self.assertIn("name",json.loads(res.data).keys())
            self.assertIn("icon",json.loads(res.data).keys())

    def test_05_validation_update_facility(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.put('/facility/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)

        # facility not found
        with self.app() as client:
            res = client.put('/facility/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Facility not found",json.loads(res.data)['message'])

        facility = Facility.query.filter_by(name=self.NAME).first()
        # name, icon blank
        with self.app() as client:
            res = client.put('/facility/crud/{}'.format(facility.id),json={'name':'','icon':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 50."],json.loads(res.data)['name'])
            self.assertListEqual(["Length must be between 3 and 40."],json.loads(res.data)['icon'])
        # invalid icon format
        with self.app() as client:
            res = client.put('/facility/crud/{}'.format(facility.id),json={'icon':'faw fa-as'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Invalid icon format."],json.loads(res.data)['icon'])

    def test_06_update_facility(self):
        facility = Facility.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.put('/facility/crud/{}'.format(facility.id),json={'name':self.NAME_2,'icon':'fa fa-test2'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success update facility.",json.loads(res.data)['message'])

    def test_07_create_another_facility(self):
        with self.app() as client:
            res = client.post('/facility/create',json={'name':self.NAME,'icon':'fa fa-test'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add facility.",json.loads(res.data)['message'])

    def test_08_name_icon_already_taken_update_facility(self):
        facility = Facility.query.filter_by(name=self.NAME_2).first()

        # name already taken
        with self.app() as client:
            res = client.put('/facility/crud/{}'.format(facility.id),json={'name':self.NAME,'icon':'fa fa-test'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["The name has already been taken."],json.loads(res.data)['name'])

        # icon already taken
        with self.app() as client:
            res = client.put('/facility/crud/{}'.format(facility.id),json={'name':self.NAME_2,'icon':'fa fa-test'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["The icon has already been taken."],json.loads(res.data)['icon'])

    def test_09_get_all_facility(self):
        # check list is not empty & no need login
        with self.app() as client:
            res = client.get('/facilities')
            self.assertEqual(200,res.status_code)
            self.assertNotEqual([],json.loads(res.data))

    def test_10_validation_delete_facility(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.delete('/facility/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # facility not found
        with self.app() as client:
            res = client.delete('/facility/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Facility not found",json.loads(res.data)['message'])

    def test_11_delete_facility_one(self):
        facility = Facility.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.delete('/facility/crud/{}'.format(facility.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete facility.",json.loads(res.data)['message'])

    def test_12_delete_facility_two(self):
        facility = Facility.query.filter_by(name=self.NAME_2).first()

        with self.app() as client:
            res = client.delete('/facility/crud/{}'.format(facility.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete facility.",json.loads(res.data)['message'])

    def test_99_delete_user_from_db(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.delete_from_db()
        user = User.query.filter_by(email=self.EMAIL_TEST_2).first()
        user.delete_from_db()
