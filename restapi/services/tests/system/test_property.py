import os, io, json
from basetest import BaseTest
from services.models.PropertyModel import Property
from services.models.UserModel import User
from services.models.RegionModel import Region

class PropertyTest(BaseTest):
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

    def test_02_validation_upload_image_create_property(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.post('/property/create',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)

        # check image is required
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,data={'images':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Missing data for required field."],json.loads(res.data)['images'])
        # check dangerous file
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images':(io.BytesIO(b"print('sa')"), 'test.py')},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Cannot identify image[1] file'],json.loads(res.data)['images'])

        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img = io.BytesIO(im.read())

        # check file extension
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images': (img, 'test.gif')},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image[1] must be jpg|png|jpeg"],json.loads(res.data)['images'])

        with open(os.path.join(self.DIR_IMAGE,'size.png'),'rb') as im:
            img = io.BytesIO(im.read())
        # file can't be grater than 4 Mb
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images': (img,'size.png')},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image[1] cannot grater than 4 Mb"],json.loads(res.data)['images'])

    def test_03_validation_create_property(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # check if data is blank
        # name,type_id,region_id,property_for,land_size,youtube,description,hotdeal,location,latitude,longitude
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                    data={'images': (img,'image.jpg'),'name':'','type_id':'','region_id':'','property_for':'',
                        'land_size':'','youtube':'','description':'','hotdeal':'',
                        'location':'','latitude':'','longitude':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Length must be between 3 and 100.'],json.loads(res.data)['name'])
            self.assertListEqual(['Not a valid integer.'],json.loads(res.data)['type_id'])
            self.assertListEqual(['Not a valid integer.'],json.loads(res.data)['region_id'])
            self.assertListEqual(['Length must be between 3 and 9.'],json.loads(res.data)['property_for'])
            self.assertListEqual(['Not a valid integer.'],json.loads(res.data)['land_size'])
            self.assertListEqual(['Length must be between 3 and 100.'],json.loads(res.data)['youtube'])
            self.assertListEqual(['Shorter than minimum length 3.'],json.loads(res.data)['description'])
            self.assertListEqual(["Not a valid boolean."],json.loads(res.data)['hotdeal'])
            self.assertListEqual(['Shorter than minimum length 3.'],json.loads(res.data)['location'])
            self.assertListEqual(['Not a valid number.'],json.loads(res.data)['latitude'])
            self.assertListEqual(['Not a valid number.'],json.loads(res.data)['longitude'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # check if type_id,region_id,land_size negative number
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images': (img,'image.jpg'),'type_id':-1,'region_id':-1,'land_size':-1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Value must be greater than 0'],json.loads(res.data)['type_id'])
            self.assertListEqual(['Value must be greater than 0'],json.loads(res.data)['region_id'])
            self.assertListEqual(['Value must be greater than 0'],json.loads(res.data)['land_size'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # check type and region not found
        # property_for must be between Sale or Rent
        # status must be between Lease Hold or Free Hold
        # period must be between annually,monthly,daily,weekly
        # invalid youtube format
        # invalid facility format
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images': (img,'image.jpg'),'type_id': 9999,'region_id': 9999,'property_for':'test',
                    'status':'test','period':'test','youtube':'youtube','facility':'a,b'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Type not found'],json.loads(res.data)['type_id'])
            self.assertListEqual(['Region not found'],json.loads(res.data)['region_id'])
            self.assertListEqual(['Property For must be between Sale or Rent'],json.loads(res.data)['property_for'])
            self.assertListEqual(['Status must be between Lease Hold or Free Hold'],json.loads(res.data)['status'])
            self.assertListEqual(['Period must be between daily, weekly, monthly, annually'],
                    json.loads(res.data)['period'])
            self.assertListEqual(['Invalid youtube format.'],json.loads(res.data)['youtube'])
            self.assertListEqual(['Invalid facility format.'],json.loads(res.data)['facility'])

        region = Region.query.filter_by(name=self.NAME).first()

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())
        # check if property_for sale status is required
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images': (img,'image.jpg'),'name':'test','type_id': 1,'region_id':region.id,
                    'property_for':'sale','land_size':1,'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                    'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['status'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # check if property_for rent period is required
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images': (img,'image.jpg'),'name':'test','type_id': 1,'region_id':region.id,
                    'property_for':'rent','land_size':1,'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                    'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['period'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # if status free hold, freehold_price is required
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images': (img,'image.jpg'),'name':'test','type_id': 1,'region_id':region.id,'status':'free hold',
                    'property_for':'sale','land_size':1,'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                    'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['freehold_price'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # if status lease hold, leasehold_price and leasehold_period is required
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images': (img,'image.jpg'),'name':'test','type_id': 1,'region_id':region.id,'status':'lease hold',
                    'property_for':'sale','land_size':1,'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                    'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['leasehold_price'])
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['leasehold_period'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # validation period - property_for rent
        # if daily exists daily_price required, until annually
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images': (img,'image.jpg'),'name':'test','type_id': 1,'region_id':region.id,
                    'property_for':'rent','period':'daily,weekly,monthly,annually','land_size':1,
                    'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                    'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['daily_price'])
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['weekly_price'])
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['monthly_price'])
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['annually_price'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # testing for property land
        # land cannot multiple status selected
        # land property must be sale only
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images': (img,'image.jpg'),'name':'test','type_id': 2,'region_id':region.id,
                    'property_for':'sale,rent','status':'free hold,lease hold','land_size':1,
                    'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                    'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Status cannot multiple select'],json.loads(res.data)['status'])
            self.assertListEqual(['Property For must be sale only'],json.loads(res.data)['property_for'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # testing for villa
        # bedroom, bathroom, facility, building_size is required
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images': (img,'image.jpg'),'name':'test','type_id': 1,'region_id':region.id,
                    'property_for':'sale','status':'free hold','land_size':1,
                    'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                    'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['bedroom'])
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['bathroom'])
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['facility'])
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['building_size'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # minimum 5 image to be upload
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images': (img,'image.jpg'),'name':'test','type_id': 1,'region_id':region.id,
                    'property_for':'sale','status':'free hold','freehold_price':1,'land_size':1,
                    'bathroom':1,'bedroom':1,'building_size':1,'facility':'0',
                    'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                    'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Minimum 5 images to be upload'],json.loads(res.data)['images'])

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

        # facility not found
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images': [(img,'image.jpg'),(img2,'image.jpg'),(img3,'image.jpg'),(img4,'image.jpg'),
                        (img5,'image.jpg')],
                'name':'test','type_id': 1,'region_id':region.id,
                'property_for':'sale','status':'free hold','freehold_price':1,'land_size':1,
                'bathroom':1,'bedroom':1,'building_size':1,'facility':'0',
                'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Facility in order 1 not found'],json.loads(res.data)['facility'])

    def test_04_create_property(self):
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

    def test_05_create_property_name_already_exists(self):
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
        # check name already taken
        with self.app() as client:
            res = client.post('/property/create',content_type=self.content_type,
                data={'images': [(img,'image.jpg'),(img2,'image.jpg'),(img3,'image.jpg'),(img4,'image.jpg'),
                        (img5,'image.jpg')],
                'name':self.NAME,'type_id': 2,'region_id':region.id,
                'property_for':'sale','status':'free hold','freehold_price':1,'land_size':1,
                'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['The name has already been taken.'],json.loads(res.data)['name'])

    def test_06_validation_upload_image_update_property(self):
        self.login(self.EMAIL_TEST_2)
        property_db = Property.query.filter_by(name=self.NAME).first()
        # check user is admin
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)

        # check images can be null
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),
                    data={},headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertNotIn("images",json.loads(res.data).keys())
        # check dangerous file
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),
                data={'images':(io.BytesIO(b"print('sa')"), 'test.py')},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Cannot identify image file'],json.loads(res.data)['images'])

        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img = io.BytesIO(im.read())

        # check file extension
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),
                data={'images': (img, 'test.gif')},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['images'])

        with open(os.path.join(self.DIR_IMAGE,'size.png'),'rb') as im:
            img = io.BytesIO(im.read())

        # file can't be grater than 4 Mb
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),
                data={'images': (img,'size.png')},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image cannot grater than 4 Mb"],json.loads(res.data)['images'])

    def test_07_validation_update_property(self):
        property_db = Property.query.filter_by(name=self.NAME).first()
        # check propery not found
        with self.app() as client:
            res = client.put('/property/crud/999999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Property not found",json.loads(res.data)['message'])

        # check if data is blank
        # name,type_id,region_id,property_for,land_size,youtube,description,hotdeal,location,latitude,longitude
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),content_type=self.content_type,
                data={'name':'','type_id':'','region_id':'','property_for':'',
                    'land_size':'','youtube':'','description':'','hotdeal':'',
                    'location':'','latitude':'','longitude':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Length must be between 3 and 100.'],json.loads(res.data)['name'])
            self.assertListEqual(['Not a valid integer.'],json.loads(res.data)['type_id'])
            self.assertListEqual(['Not a valid integer.'],json.loads(res.data)['region_id'])
            self.assertListEqual(['Length must be between 3 and 9.'],json.loads(res.data)['property_for'])
            self.assertListEqual(['Not a valid integer.'],json.loads(res.data)['land_size'])
            self.assertListEqual(['Length must be between 3 and 100.'],json.loads(res.data)['youtube'])
            self.assertListEqual(['Shorter than minimum length 3.'],json.loads(res.data)['description'])
            self.assertListEqual(["Not a valid boolean."],json.loads(res.data)['hotdeal'])
            self.assertListEqual(['Shorter than minimum length 3.'],json.loads(res.data)['location'])
            self.assertListEqual(['Not a valid number.'],json.loads(res.data)['latitude'])
            self.assertListEqual(['Not a valid number.'],json.loads(res.data)['longitude'])

        # check if type_id,region_id,land_size negative number
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),content_type=self.content_type,
                data={'type_id':-1,'region_id':-1,'land_size':-1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Value must be greater than 0'],json.loads(res.data)['type_id'])
            self.assertListEqual(['Value must be greater than 0'],json.loads(res.data)['region_id'])
            self.assertListEqual(['Value must be greater than 0'],json.loads(res.data)['land_size'])

        # check type and region not found
        # property_for must be between Sale or Rent
        # status must be between Lease Hold or Free Hold
        # period must be between annually,monthly,daily,weekly
        # invalid youtube format
        # invalid facility format
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),content_type=self.content_type,
                data={'type_id': 9999,'region_id': 9999,'property_for':'test',
                    'status':'test','period':'test','youtube':'youtube','facility':'a,b'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Type not found'],json.loads(res.data)['type_id'])
            self.assertListEqual(['Region not found'],json.loads(res.data)['region_id'])
            self.assertListEqual(['Property For must be between Sale or Rent'],json.loads(res.data)['property_for'])
            self.assertListEqual(['Status must be between Lease Hold or Free Hold'],json.loads(res.data)['status'])
            self.assertListEqual(['Period must be between daily, weekly, monthly, annually'],
                    json.loads(res.data)['period'])
            self.assertListEqual(['Invalid youtube format.'],json.loads(res.data)['youtube'])
            self.assertListEqual(['Invalid facility format.'],json.loads(res.data)['facility'])

        region = Region.query.filter_by(name=self.NAME).first()
        # check if property_for sale status is required
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),content_type=self.content_type,
                data={'name':'test','type_id': 1,'region_id':region.id,
                    'property_for':'sale','land_size':1,'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                    'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['status'])

        # check if property_for rent period is required
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),content_type=self.content_type,
                data={'name':'test','type_id': 1,'region_id':region.id,
                    'property_for':'rent','land_size':1,'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                    'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['period'])

        # if status free hold, freehold_price is required
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),content_type=self.content_type,
                data={'name':'test','type_id': 1,'region_id':region.id,'status':'free hold',
                    'property_for':'sale','land_size':1,'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                    'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['freehold_price'])

        # if status lease hold, leasehold_price and leasehold_period is required
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),content_type=self.content_type,
                data={'name':'test','type_id': 1,'region_id':region.id,'status':'lease hold',
                    'property_for':'sale','land_size':1,'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                    'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['leasehold_price'])
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['leasehold_period'])

        # validation period - property_for rent
        # if daily exists daily_price required, until annually
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),content_type=self.content_type,
                data={'name':'test','type_id': 1,'region_id':region.id,
                    'property_for':'rent','period':'daily,weekly,monthly,annually','land_size':1,
                    'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                    'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['daily_price'])
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['weekly_price'])
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['monthly_price'])
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['annually_price'])

        # testing for property land
        # land cannot multiple status selected
        # land property must be sale only
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),content_type=self.content_type,
                data={'name':'test','type_id': 2,'region_id':region.id,
                    'property_for':'sale,rent','status':'free hold,lease hold','land_size':1,
                    'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                    'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Status cannot multiple select'],json.loads(res.data)['status'])
            self.assertListEqual(['Property For must be sale only'],json.loads(res.data)['property_for'])

        # testing for villa
        # bedroom, bathroom, facility, building_size is required
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),content_type=self.content_type,
                data={'name':'test','type_id': 1,'region_id':region.id,
                    'property_for':'sale','status':'free hold','land_size':1,
                    'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                    'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['bedroom'])
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['bathroom'])
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['facility'])
            self.assertListEqual(['Missing data for required field.'],json.loads(res.data)['building_size'])

        # facility not found
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),content_type=self.content_type,
                data={'name':'test','type_id': 1,'region_id':region.id,
                'property_for':'sale','status':'free hold','freehold_price':1,'land_size':1,
                'bathroom':1,'bedroom':1,'building_size':1,'facility':'0',
                'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Facility in order 1 not found'],json.loads(res.data)['facility'])

    def test_08_update_property(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        property_db = Property.query.filter_by(name=self.NAME).first()
        region = Region.query.filter_by(name=self.NAME).first()
        # success update property
        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),content_type=self.content_type,
                data={'images':(img,'image.jpg'),'name':self.NAME,'type_id': 2,'region_id':region.id,
                'property_for':'sale','status':'free hold','freehold_price':1,'land_size':1,
                'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo','description':'asdasd',
                'hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success update property.",json.loads(res.data)['message'])

    def test_09_create_another_property(self):
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
                'name':self.NAME_2,'type_id': 2,'region_id':region.id,
                'property_for':'sale','status':'free hold','freehold_price':1,'land_size':1,
                'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo',
                'description':'asdasd','hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add property.",json.loads(res.data)['message'])

    def test_10_can_update_name_if_same_with_previous_property(self):
        property_db = Property.query.filter_by(name=self.NAME).first()
        region = Region.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),content_type=self.content_type,
                data={'name':self.NAME,'type_id': 2,'region_id':region.id,
                'property_for':'sale','status':'free hold','freehold_price':1,'land_size':1,
                'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo','description':'asdasd',
                'hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success update property.",json.loads(res.data)['message'])

    def test_11_update_property_name_already_exists(self):
        property_db = Property.query.filter_by(name=self.NAME).first()
        region = Region.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.put('/property/crud/{}'.format(property_db.id),content_type=self.content_type,
                data={'name':self.NAME_2,'type_id': 2,'region_id':region.id,
                'property_for':'sale','status':'free hold','freehold_price':1,'land_size':1,
                'youtube':'https://www.youtube.com/watch?v=jXYKhZCvWEo','description':'asdasd',
                'hotdeal':False,'location':'bali','latitude':1,'longitude':1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['The name has already been taken.'],json.loads(res.data)['name'])

    def test_12_validation_delete_image_property(self):
        self.login(self.EMAIL_TEST_2)
        property_db = Property.query.filter_by(name=self.NAME).first()
        # check user is admin
        with self.app() as client:
            res = client.post('/property/delete-images/{}'.format(property_db.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # property not found
        with self.app() as client:
            res = client.post('/property/delete-images/999999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Property not found",json.loads(res.data)['message'])
        # check images is blank
        with self.app() as client:
            res = client.post('/property/delete-images/{}'.format(property_db.id),
                json={'images':''},headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Not a valid list."],json.loads(res.data)['images'])
        # check images list is blank
        with self.app() as client:
            res = client.post('/property/delete-images/{}'.format(property_db.id),
                json={'images':[]},headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Shorter than minimum length 1."],json.loads(res.data)['images'])
        # check valid url format
        with self.app() as client:
            res = client.post('/property/delete-images/{}'.format(property_db.id),
                json={'images':['asd']},headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Not a valid URL."],json.loads(res.data)['images']['0'])

    def test_13_delete_image_property(self):
        property_db = Property.query.filter_by(name=self.NAME).first()
        images = [f"http://localhost:5000/static/properties/{property_db.slug}/{property_db.images.split(',')[0]}"]

        with self.app() as client:
            res = client.post('/property/delete-images/{}'.format(property_db.id),
                json={'images': images},headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete image.",json.loads(res.data)['message'])

    def test_14_delete_image_property_cannot_delete_under_5_image(self):
        property_db = Property.query.filter_by(name=self.NAME).first()
        images = [f"http://localhost:5000/static/properties/{property_db.slug}/{property_db.images.split(',')[0]}"]

        with self.app() as client:
            res = client.post('/property/delete-images/{}'.format(property_db.id),
                json={'images': images},headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['Minimum 5 images to be upload'],json.loads(res.data)['images'])

    def test_15_get_all_property(self):
        # check list is not empty & no need login
        with self.app() as client:
            res = client.get('/properties')
            self.assertEqual(200,res.status_code)
            self.assertNotEqual({},json.loads(res.data))

    def test_16_get_property_by_id(self):
        self.login(self.EMAIL_TEST_2)

        property_db = Property.query.filter_by(name=self.NAME).first()
        # check user is admin
        with self.app() as client:
            res = client.get('/property/crud/{}'.format(property_db.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # property not found
        with self.app() as client:
            res = client.get('/property/crud/99999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Property not found",json.loads(res.data)['message'])
        # get specific property
        with self.app() as client:
            res = client.get('/property/crud/{}'.format(property_db.id),
                    headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertIn('id',json.loads(res.data).keys())
            self.assertIn('name',json.loads(res.data).keys())
            self.assertIn('slug',json.loads(res.data).keys())
            self.assertIn('images',json.loads(res.data).keys())
            self.assertIn('property_for',json.loads(res.data).keys())
            self.assertIn('period',json.loads(res.data).keys())
            self.assertIn('status',json.loads(res.data).keys())
            self.assertIn('youtube',json.loads(res.data).keys())
            self.assertIn('description',json.loads(res.data).keys())
            self.assertIn('hotdeal',json.loads(res.data).keys())
            self.assertIn('bedroom',json.loads(res.data).keys())
            self.assertIn('bathroom',json.loads(res.data).keys())
            self.assertIn('building_size',json.loads(res.data).keys())
            self.assertIn('land_size',json.loads(res.data).keys())
            self.assertIn('location',json.loads(res.data).keys())
            self.assertIn('latitude',json.loads(res.data).keys())
            self.assertIn('longitude',json.loads(res.data).keys())
            self.assertIn('created_at',json.loads(res.data).keys())
            self.assertIn('updated_at',json.loads(res.data).keys())
            self.assertIn('type_id',json.loads(res.data).keys())
            self.assertIn('region_id',json.loads(res.data).keys())
            self.assertIn('price',json.loads(res.data).keys())
            self.assertIn('facilities',json.loads(res.data).keys())

    def test_17_property_by_slug(self):
        # note this endpoint is public data
        # activity not found
        with self.app() as client:
            res = client.get('/property/ngawur')
            self.assertEqual(404,res.status_code)
            self.assertEqual("Property not found",json.loads(res.data)['message'])

        property_db = Property.query.filter_by(name=self.NAME).first()
        with self.app() as client:
            res = client.get('/property/{}'.format(property_db.slug))
            self.assertEqual(200,res.status_code)
            self.assertIn('id',json.loads(res.data).keys())
            self.assertIn('name',json.loads(res.data).keys())
            self.assertIn('slug',json.loads(res.data).keys())
            self.assertIn('images',json.loads(res.data).keys())
            self.assertIn('property_for',json.loads(res.data).keys())
            self.assertIn('period',json.loads(res.data).keys())
            self.assertIn('status',json.loads(res.data).keys())
            self.assertIn('youtube',json.loads(res.data).keys())
            self.assertIn('description',json.loads(res.data).keys())
            self.assertIn('hotdeal',json.loads(res.data).keys())
            self.assertIn('bedroom',json.loads(res.data).keys())
            self.assertIn('bathroom',json.loads(res.data).keys())
            self.assertIn('building_size',json.loads(res.data).keys())
            self.assertIn('land_size',json.loads(res.data).keys())
            self.assertIn('location',json.loads(res.data).keys())
            self.assertIn('latitude',json.loads(res.data).keys())
            self.assertIn('longitude',json.loads(res.data).keys())
            self.assertIn('created_at',json.loads(res.data).keys())
            self.assertIn('updated_at',json.loads(res.data).keys())
            self.assertIn('type_id',json.loads(res.data).keys())
            self.assertIn('region_id',json.loads(res.data).keys())
            self.assertIn('price',json.loads(res.data).keys())
            self.assertIn('facilities',json.loads(res.data).keys())
            self.assertIn('seen',json.loads(res.data).keys())
            self.assertIn('similar_listing',json.loads(res.data).keys())

    def test_18_search_property_by_location(self):
        # type not found
        with self.app() as client:
            res = client.get('/property/search-by-location?q=a&type_id=99999')
            self.assertEqual(404,res.status_code)
            self.assertEqual("Type not found",json.loads(res.data)['message'])

        with self.app() as client:
            res = client.get('/property/search-by-location?q=a&type_id=2')
            self.assertEqual(200,res.status_code)
            self.assertNotEqual([],json.loads(res.data))

    def test_19_validation_delete_property(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.delete('/property/crud/1',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # property not found
        with self.app() as client:
            res = client.delete('/property/crud/999999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Property not found",json.loads(res.data)['message'])

    def test_20_delete_property_one(self):
        property_db = Property.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.delete('/property/crud/{}'.format(property_db.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete property.",json.loads(res.data)['message'])

    def test_21_delete_property_two(self):
        property_db = Property.query.filter_by(name=self.NAME_2).first()

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
