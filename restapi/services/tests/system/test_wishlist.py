import os, io, json
from basetest import BaseTest
from services.models.UserModel import User
from services.models.RegionModel import Region
from services.models.PropertyModel import Property

class WishlistTest(BaseTest):
    def test_00_add_2_user(self):
        self.register(self.EMAIL_TEST,'asd')
        self.register(self.EMAIL_TEST_2,'asd2')

        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST).first())
        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST_2).first())

    def test_01_create_region(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.role = 2
        user.save_to_db()
        # login user 1
        self.login(self.EMAIL_TEST)

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.post('/region/create',content_type=self.content_type,
                data={'image': (img,'image.jpg'),'name': self.NAME,'description':'asdasd'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add region.",json.loads(res.data)['message'])

    def test_02_create_property(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img2 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img3 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img4 = io.BytesIO(im.read())
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img5 = io.BytesIO(im.read())

        region = Region.query.filter_by(name=self.NAME).first()
        # success add property
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images': [(img,'image.jpg'),(img2,'image.jpg'),(img3,'image.jpg'),(img4,'image.jpg'),
                        (img5,'image.jpg')],
                'name':self.NAME,'type_id': 2,'region_id':region.id,
                'property_for':'sale','status':'free hold','freehold_price':1,'land_size':1,
                'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add property.",json.loads(res.data)['message'])

    def test_03_validation_love_property(self):
        # property not found
        with self.app() as client:
            res = client.post('/wishlist/love/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual('Property not found',json.loads(res.data)['message'])

    def test_04_love_property(self):
        property_db = Property.query.filter_by(name=self.NAME).first()
        # success add property in wishlist
        with self.app() as client:
            res = client.post('/wishlist/love/{}'.format(property_db.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual('Property entered into the wishlist',json.loads(res.data)['message'])

    def test_05_get_current_user_wishlist(self):
        with self.app() as client:
            res = client.get('/wishlist/user',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertNotEqual([],json.loads(res.data))

    def test_06_love_property_already_in_wishlist(self):
        property_db = Property.query.filter_by(name=self.NAME).first()
        # property already in wishlist
        with self.app() as client:
            res = client.post('/wishlist/love/{}'.format(property_db.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual('Property already in wishlist',json.loads(res.data)['message'])

    def test_07_validation_unlove_property(self):
        # property not found
        with self.app() as client:
            res = client.delete('/wishlist/unlove/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual('Property not found',json.loads(res.data)['message'])

    def test_08_unlove_property(self):
        property_db = Property.query.filter_by(name=self.NAME).first()
        # success remove property in wishlist
        with self.app() as client:
            res = client.delete('/wishlist/unlove/{}'.format(property_db.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual('Property remove from wishlist',json.loads(res.data)['message'])

    def test_09_unlove_property_already_in_wishlist(self):
        property_db = Property.query.filter_by(name=self.NAME).first()
        # property not on wishlist
        with self.app() as client:
            res = client.delete('/wishlist/unlove/{}'.format(property_db.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual('Property not on wishlist',json.loads(res.data)['message'])

    def test_97_delete_property(self):
        property_db = Property.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.delete('/property/crud/{}'.format(property_db.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete property.",json.loads(res.data)['message'])

    def test_98_delete_region(self):
        region = Region.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.delete('/region/crud/{}'.format(region.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete region.",json.loads(res.data)['message'])

    def test_99_delete_user_from_db(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.delete_from_db()
        user = User.query.filter_by(email=self.EMAIL_TEST_2).first()
        user.delete_from_db()
