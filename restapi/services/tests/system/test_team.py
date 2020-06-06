import json, io, os
from basetest import BaseTest
from services.models.UserModel import User
from services.models.TeamModel import Team

class TeamTest(BaseTest):
    def test_00_add_2_user(self):
        self.register(self.EMAIL_TEST,'asd')
        self.register(self.EMAIL_TEST_2,'asd2')

        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST).first())
        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST_2).first())

    def test_01_validation_create_team(self):
        self.login(self.EMAIL_TEST_2)
        # can't access without role admin
        with self.app() as client:
            res = client.post('/team/create',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.role = 2
        user.save_to_db()
        # login user 1
        self.login(self.EMAIL_TEST)

        # check image required
        with self.app() as client:
            res = client.post('/team/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Missing data for required field."],json.loads(res.data)['image'])
        # check dangerous file
        with self.app() as client:
            res = client.post('/team/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (io.BytesIO(b"print('sa')"), 'test.py')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Cannot identify image file"],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img = io.BytesIO(im.read())
        # check file extension
        with self.app() as client:
            res = client.post('/team/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (img,'test.gif')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'size.png'),'rb') as im:
            img = io.BytesIO(im.read())
        # file can't be grater than 4 Mb
        with self.app() as client:
            res = client.post('/team/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (img,'size.png')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image cannot grater than 4 Mb"],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        # name, title, phone blank
        with self.app() as client:
            res = client.post('/team/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img,'image.jpg'),'name':'','title':'','phone':''})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['name'])
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['title'])
            self.assertListEqual(["Not a valid number."],json.loads(res.data)['phone'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())
        # check phone negative number
        with self.app() as client:
            res = client.post('/team/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img,'image.jpg'),'phone':-1})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Value must be greater than 0"],json.loads(res.data)['phone'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())
        # invalid phone number
        with self.app() as client:
            res = client.post('/team/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img,'image.jpg'),'phone':'08786233dwq231'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Not a valid number."],json.loads(res.data)['phone'])

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())
        # length phone number between 3 to 20
        with self.app() as client:
            res = client.post('/team/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img,'image.jpg'),'phone':'08'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 20."],json.loads(res.data)['phone'])

    def test_02_create_team(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.post('/team/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img,'image.jpg'),'name':self.NAME,'title':self.NAME,'phone':'87862371'})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add team.",json.loads(res.data)['message'])

    def test_03_create_team_name_already_exists(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.post('/team/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img,'image.jpg'),'name':self.NAME,'title':self.NAME,'phone':'87862371'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(['The name has already been taken.'],json.loads(res.data)['name'])

    def test_04_get_team_by_id(self):
        # check user is admin
        self.login(self.EMAIL_TEST_2)
        with self.app() as client:
            res = client.get('/team/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # team not found
        with self.app() as client:
            res = client.get('/team/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Team not found",json.loads(res.data)['message'])
        # get specific team
        team = Team.query.filter_by(name=self.NAME).first()
        with self.app() as client:
            res = client.get('/team/crud/{}'.format(team.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertIn("id",json.loads(res.data).keys())
            self.assertIn("name",json.loads(res.data).keys())
            self.assertIn("title",json.loads(res.data).keys())
            self.assertIn("image",json.loads(res.data).keys())
            self.assertIn("phone",json.loads(res.data).keys())

    def test_05_validation_update_team(self):
        self.login(self.EMAIL_TEST_2)
        # can't access without role admin
        with self.app() as client:
            res = client.put('/team/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.role = 2
        user.save_to_db()
        # login user 1
        self.login(self.EMAIL_TEST)

        # team not found
        with self.app() as client:
            res = client.put('/team/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Team not found",json.loads(res.data)['message'])

        team = Team.query.filter_by(name=self.NAME).first()
        # name, title, phone blank & image can be null
        with self.app() as client:
            res = client.put('/team/crud/{}'.format(team.id),
                content_type=self.content_type,data={'image':'','name':'','title':'','phone':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['name'])
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['title'])
            self.assertListEqual(["Not a valid number."],json.loads(res.data)['phone'])

        # check phone negative number
        with self.app() as client:
            res = client.put('/team/crud/{}'.format(team.id),content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'phone':-1})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Value must be greater than 0"],json.loads(res.data)['phone'])

        # invalid phone number
        with self.app() as client:
            res = client.put('/team/crud/{}'.format(team.id),content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'phone':'08786233dwq231'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Not a valid number."],json.loads(res.data)['phone'])

        # length phone number between 3 to 20
        with self.app() as client:
            res = client.put('/team/crud/{}'.format(team.id),content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'phone':'08'})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 20."],json.loads(res.data)['phone'])

        # check dangerous file
        with self.app() as client:
            res = client.put('/team/crud/{}'.format(team.id),content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (io.BytesIO(b"print('sa')"), 'test.py')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Cannot identify image file"],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'test.gif'),'rb') as im:
            img = io.BytesIO(im.read())
        # check file extension
        with self.app() as client:
            res = client.put('/team/crud/{}'.format(team.id),content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (img,'test.gif')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image must be jpg|png|jpeg"],json.loads(res.data)['image'])

        with open(os.path.join(self.DIR_IMAGE,'size.png'),'rb') as im:
            img = io.BytesIO(im.read())
        # file can't be grater than 4 Mb
        with self.app() as client:
            res = client.put('/team/crud/{}'.format(team.id),content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image': (img,'size.png')})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Image cannot grater than 4 Mb"],json.loads(res.data)['image'])

    def test_06_update_team(self):
        team = Team.query.filter_by(name=self.NAME).first()

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.put('/team/crud/{}'.format(team.id),content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img,'image.jpg'),'name':self.NAME_2,'title':self.NAME_2,'phone':'87862371'})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success update team.",json.loads(res.data)['message'])

    def test_07_create_another_team(self):
        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.post('/team/create',content_type=self.content_type,
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"},
                data={'image':(img,'image.jpg'),'name':self.NAME,'title':self.NAME,'phone':'87862371'})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add team.",json.loads(res.data)['message'])

    def test_08_name_already_exists_update_team(self):
        team = Team.query.filter_by(name=self.NAME_2).first()

        with open(os.path.join(self.DIR_IMAGE,'image.jpg'),'rb') as im:
            img = io.BytesIO(im.read())

        with self.app() as client:
            res = client.put('/team/crud/{}'.format(team.id),content_type=self.content_type,
                data={'image': (img,'image.jpg'),'name': self.NAME,'title': self.NAME,'phone':'87862371'},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["The name has already been taken."],json.loads(res.data)['name'])

    def test_09_validation_delete_team(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.delete('/team/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # team not found
        with self.app() as client:
            res = client.delete('/team/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Team not found",json.loads(res.data)['message'])

    def test_10_delete_team_one(self):
        team = Team.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.delete('/team/crud/{}'.format(team.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete team.",json.loads(res.data)['message'])

    def test_11_delete_team_two(self):
        team = Team.query.filter_by(name=self.NAME_2).first()

        with self.app() as client:
            res = client.delete('/team/crud/{}'.format(team.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete team.",json.loads(res.data)['message'])

    def test_99_delete_user_from_db(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.delete_from_db()
        user = User.query.filter_by(email=self.EMAIL_TEST_2).first()
        user.delete_from_db()
