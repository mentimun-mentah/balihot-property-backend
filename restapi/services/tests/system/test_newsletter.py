import json, io, os
from basetest import BaseTest
from services.models.UserModel import User
from services.models.NewsletterModel import Newsletter

class NewsletterTest(BaseTest):
    def test_00_add_2_user(self):
        self.register(self.EMAIL_TEST,'asd')
        self.register(self.EMAIL_TEST_2,'asd2')

        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST).first())
        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST_2).first())

    def test_01_validation_create_newsletter(self):
        self.login(self.EMAIL_TEST_2)
        # can't access without role admin
        with self.app() as client:
            res = client.post('/newsletter/create',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.role = 2
        user.save_to_db()
        # login user 1
        self.login(self.EMAIL_TEST)

        # check image required
        with self.app() as client:
            res = client.post('/newsletter/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Missing data for required field."],json.loads(res.data)['image'])

        # check dangerous file
        with self.app() as client:
            res = client.post('/newsletter/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (io.BytesIO(b"print('sa')"), 'test.py')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Cannot identify image file"],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img = io.BytesIO(im.read())

        # check file extension
        with self.app() as client:
            res = client.post('/newsletter/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (img,'test.gif')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'size12mb.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # file can't be grater than 6 Mb
        with self.app() as client:
            res = client.post('/newsletter/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (img,'size12mb.jpg')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image cannot grater than 6 Mb"],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # title, description blank
        with self.app() as client:
            res = client.post('/newsletter/create',content_type=self.content_type,
                data={'image': (img,'image.jpg'),'title':'','description':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['title'])
            self.assertListEqual(['Shorter than minimum length 3.'],json.loads(res.data)['description'])

    def test_02_create_newsletter(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.post('/newsletter/create',content_type=self.content_type,
                data={'image': (img,'image.jpg'),'title': self.NAME,'description':'asdasd'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add newsletter.",json.loads(res.data)['message'])

    def test_03_name_already_taken_create_newsletter(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.post('/newsletter/create',content_type=self.content_type,
                data={'image': (img,'image.jpg'),'title': self.NAME,'description':'asdasd'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['The title has already been taken.'],json.loads(res.data)['title'])

    def test_04_get_newsletter_by_id(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.get('/newsletter/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # newsletter not found
        with self.app() as client:
            res = client.get('/newsletter/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Newsletter not found",json.loads(res.data)['message'])
        # get specific newsletter
        newsletter = Newsletter.query.filter_by(title=self.NAME).first()
        with self.app() as client:
            res = client.get('/newsletter/crud/{}'.format(newsletter.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertIn("id",json.loads(res.data).keys())
            self.assertIn("title",json.loads(res.data).keys())
            self.assertIn("slug",json.loads(res.data).keys())
            self.assertIn("image",json.loads(res.data).keys())
            self.assertIn("thumbnail",json.loads(res.data).keys())
            self.assertIn("description",json.loads(res.data).keys())
            self.assertIn("created_at",json.loads(res.data).keys())
            self.assertIn("updated_at",json.loads(res.data).keys())

    def test_05_validation_update_newsletter(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.put('/newsletter/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)

        # newsletter not found
        with self.app() as client:
            res = client.put('/newsletter/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Newsletter not found",json.loads(res.data)['message'])

        newsletter = Newsletter.query.filter_by(title=self.NAME).first()
        # title, description & image can be null
        with self.app() as client:
            res = client.put('/newsletter/crud/{}'.format(newsletter.id),content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':'','title':'','description':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['title'])
            self.assertListEqual(['Shorter than minimum length 3.'],json.loads(res.data)['description'])

        # check dangerous file
        with self.app() as client:
            res = client.put('/newsletter/crud/{}'.format(newsletter.id),content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (io.BytesIO(b"print('sa')"), 'test.py')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Cannot identify image file"],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img = io.BytesIO(im.read())

        # check file extension
        with self.app() as client:
            res = client.put('/newsletter/crud/{}'.format(newsletter.id),content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (img,'test.gif')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'size12mb.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # file can't be grater than 6 Mb
        with self.app() as client:
            res = client.put('/newsletter/crud/{}'.format(newsletter.id),content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (img,'size12mb.jpg')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image cannot grater than 6 Mb"],json.loads(res.data)['image'])

    def test_06_update_newsletter(self):
        newsletter = Newsletter.query.filter_by(title=self.NAME).first()

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.put('/newsletter/crud/{}'.format(newsletter.id),content_type=self.content_type,
                data={'image': (img,'image.jpg'),'title': self.NAME_2,'description':'asdasd'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success update newsletter.",json.loads(res.data)['message'])

    def test_07_create_another_newsletter(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.post('/newsletter/create',content_type=self.content_type,
                data={'image': (img,'image.jpg'),'title': self.NAME,'description':'asdasd'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add newsletter.",json.loads(res.data)['message'])

    def test_08_name_already_exists_update_newsletter(self):
        newsletter = Newsletter.query.filter_by(title=self.NAME_2).first()

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.put('/newsletter/crud/{}'.format(newsletter.id),content_type=self.content_type,
                data={'image': (img,'image.jpg'),'title': self.NAME,'description':'asdasd'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["The title has already been taken."],json.loads(res.data)['title'])

    def test_09_get_all_newsletter(self):
        # check list is not empty & no need login
        with self.app() as client:
            res = client.get('/newsletters')
            self.assertEqual(200,res.status_code)
            self.assertNotEqual({},json.loads(res.data))

    def test_10_search_newsletter_by_title(self):
        with self.app() as client:
            res = client.get('/newsletter/search-by-title?q=a')
            self.assertEqual(200,res.status_code)
            self.assertNotEqual([],json.loads(res.data))

    def test_11_newsletter_by_slug(self):
        # note this endpoint is public data
        # newsletter not found
        with self.app() as client:
            res = client.get('/newsletter/ngawur')
            self.assertEqual(404,res.status_code)
            self.assertEqual("Newsletter not found",json.loads(res.data)['message'])

        newsletter = Newsletter.query.filter_by(title=self.NAME).first()
        with self.app() as client:
            res = client.get('/newsletter/{}'.format(newsletter.slug))
            self.assertEqual(200,res.status_code)
            self.assertIn("id",json.loads(res.data).keys())
            self.assertIn("title",json.loads(res.data).keys())
            self.assertIn("slug",json.loads(res.data).keys())
            self.assertIn("image",json.loads(res.data).keys())
            self.assertIn("thumbnail",json.loads(res.data).keys())
            self.assertIn("description",json.loads(res.data).keys())
            self.assertIn("created_at",json.loads(res.data).keys())
            self.assertIn("updated_at",json.loads(res.data).keys())
            self.assertIn("seen",json.loads(res.data).keys())

    def test_12_newsletter_most_popular(self):
        with self.app() as client:
            res = client.get('/newsletter/most-popular')
            self.assertEqual(200,res.status_code)
            self.assertTrue(type(json.loads(res.data)) is list)

    def test_13_validation_delete_newsletter(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.delete('/newsletter/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # newsletter not found
        with self.app() as client:
            res = client.delete('/newsletter/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Newsletter not found",json.loads(res.data)['message'])

    def test_14_delete_newsletter_one(self):
        newsletter = Newsletter.query.filter_by(title=self.NAME).first()

        with self.app() as client:
            res = client.delete('/newsletter/crud/{}'.format(newsletter.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete newsletter.",json.loads(res.data)['message'])

    def test_15_delete_newsletter_two(self):
        newsletter = Newsletter.query.filter_by(title=self.NAME_2).first()

        with self.app() as client:
            res = client.delete('/newsletter/crud/{}'.format(newsletter.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete newsletter.",json.loads(res.data)['message'])

    def test_99_delete_user_from_db(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.delete_from_db()
        user = User.query.filter_by(email=self.EMAIL_TEST_2).first()
        user.delete_from_db()
