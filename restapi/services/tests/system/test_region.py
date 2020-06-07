import json, os, io
from basetest import BaseTest
from services.models.UserModel import User
from services.models.RegionModel import Region

class RegionTest(BaseTest):
    def test_00_add_2_user(self):
        self.register(self.EMAIL_TEST,'asd')
        self.register(self.EMAIL_TEST_2,'asd2')

        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST).first())
        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST_2).first())

    def test_01_validation_create_region(self):
        self.login(self.EMAIL_TEST_2)
        # can't access without role admin
        with self.app() as client:
            res = client.post('/region/create',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.role = 2
        user.save_to_db()
        # login user 1
        self.login(self.EMAIL_TEST)

        # check image required
        with self.app() as client:
            res = client.post('/region/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Missing data for required field."],json.loads(res.data)['image'])

        # check dangerous file
        with self.app() as client:
            res = client.post('/region/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (io.BytesIO(b"print('sa')"), 'test.py')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Cannot identify image file"],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img = io.BytesIO(im.read())
        # check file extension
        with self.app() as client:
            res = client.post('/region/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (img,'test.gif')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'size.png'),'rb') as im:
            img = io.BytesIO(im.read())
        # file can't be grater than 4 Mb
        with self.app() as client:
            res = client.post('/region/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (img,'size.png')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image cannot grater than 4 Mb"],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # name blank
        with self.app() as client:
            res = client.post('/region/create',content_type=self.content_type,
                data={'image': (img,'image.jpg'),'name':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['name'])

    def test_02_create_region(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.post('/region/create',content_type=self.content_type,
                data={'image': (img,'image.jpg'),'name': self.NAME},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add region.",json.loads(res.data)['message'])

    def test_03_name_already_taken_create_region(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.post('/region/create',content_type=self.content_type,
                data={'image': (img,'image.jpg'),'name': self.NAME},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['The name has already been taken.'],json.loads(res.data)['name'])

    def test_04_get_region_by_id(self):
        # check user is admin
        self.login(self.EMAIL_TEST_2)
        with self.app() as client:
            res = client.get('/region/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # region not found
        with self.app() as client:
            res = client.get('/region/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Region not found",json.loads(res.data)['message'])
        # get specific region
        region = Region.query.filter_by(name=self.NAME).first()
        with self.app() as client:
            res = client.get('/region/crud/{}'.format(region.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertIn("id",json.loads(res.data).keys())
            self.assertIn("name",json.loads(res.data).keys())
            self.assertIn("image",json.loads(res.data).keys())

    def test_05_validation_update_region(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.put('/region/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)

        # region not found
        with self.app() as client:
            res = client.put('/region/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Region not found",json.loads(res.data)['message'])

        # name blank & image can be null
        region = Region.query.filter_by(name=self.NAME).first()
        with self.app() as client:
            res = client.put('/region/crud/{}'.format(region.id),content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':'','name':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['name'])

        # check dangerous file
        with self.app() as client:
            res = client.put('/region/crud/{}'.format(region.id),content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (io.BytesIO(b"print('sa')"), 'test.py')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Cannot identify image file"],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img = io.BytesIO(im.read())
        # check file extension
        with self.app() as client:
            res = client.put('/region/crud/{}'.format(region.id),content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (img,'test.gif')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'size.png'),'rb') as im:
            img = io.BytesIO(im.read())
        # file can't be grater than 4 Mb
        with self.app() as client:
            res = client.put('/region/crud/{}'.format(region.id),content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (img,'size.png')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image cannot grater than 4 Mb"],json.loads(res.data)['image'])

    def test_06_update_region(self):
        region = Region.query.filter_by(name=self.NAME).first()

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.put('/region/crud/{}'.format(region.id),content_type=self.content_type,
                data={'image': (img,'image.jpg'),'name': self.NAME_2},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success update region.",json.loads(res.data)['message'])

    def test_07_create_another_region(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.post('/region/create',content_type=self.content_type,
                data={'image': (img,'image.jpg'),'name': self.NAME},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add region.",json.loads(res.data)['message'])

    def test_08_name_already_exists_update_region(self):
        region = Region.query.filter_by(name=self.NAME_2).first()

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.put('/region/crud/{}'.format(region.id),content_type=self.content_type,
                data={'image': (img,'image.jpg'),'name': self.NAME},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["The name has already been taken."],json.loads(res.data)['name'])

    def test_09_get_all_region(self):
        # check list is not empty & no need login
        with self.app() as client:
            res = client.get('/regions')
            self.assertEqual(200,res.status_code)
            self.assertNotEqual([],json.loads(res.data))

    def test_10_validation_delete_region(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.delete('/region/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # region not found
        with self.app() as client:
            res = client.delete('/region/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Region not found",json.loads(res.data)['message'])

    def test_11_delete_region_one(self):
        region = Region.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.delete('/region/crud/{}'.format(region.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete region.",json.loads(res.data)['message'])

    def test_12_delete_region_two(self):
        region = Region.query.filter_by(name=self.NAME_2).first()

        with self.app() as client:
            res = client.delete('/region/crud/{}'.format(region.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete region.",json.loads(res.data)['message'])

    def test_99_delete_user_from_db(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.delete_from_db()
        user = User.query.filter_by(email=self.EMAIL_TEST_2).first()
        user.delete_from_db()
