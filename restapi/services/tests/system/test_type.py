import json
from basetest import BaseTest
from services.models.UserModel import User
from services.models.TypeModel import Type
from services.models.CategoryModel import Category

class TypeTest(BaseTest):
    def test_00_add_2_user(self):
        self.register(self.EMAIL_TEST,'asd')
        self.register(self.EMAIL_TEST_2,'asd2')

        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST).first())
        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST_2).first())

    def test_01_create_category(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.role = 2
        user.save_to_db()
        # login user 1
        self.login(self.EMAIL_TEST)

        with self.app() as client:
            res = client.post('/category/create',json={'name':self.NAME},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add category.",json.loads(res.data)['message'])

    def test_02_validation_create_type(self):
        self.login(self.EMAIL_TEST_2)
        # can't access without role admin
        with self.app() as client:
            res = client.post('/type/create',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        # login user 1
        self.login(self.EMAIL_TEST)

        # name, category_id blank
        with self.app() as client:
            res = client.post('/type/create',json={'name':'','category_id':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['name'])
            self.assertListEqual(["Not a valid integer."],json.loads(res.data)['category_id'])
        # check category_id negative number
        with self.app() as client:
            res = client.post('/type/create',json={'category_id':-1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Value must be greater than 0"],json.loads(res.data)['category_id'])
        # category_id not found
        with self.app() as client:
            res = client.post('/type/create',json={'category_id':99999},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Category not found"],json.loads(res.data)['category_id'])

    def test_03_create_type(self):
        category = Category.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.post('/type/create',json={'name': self.NAME,'category_id':category.id},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add type.",json.loads(res.data)['message'])

    def test_04_name_already_taken_create_type(self):
        category = Category.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.post('/type/create',json={'name': self.NAME,'category_id':category.id},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["The name has already been taken."],json.loads(res.data)['name'])

    def test_05_get_type_by_id(self):
        # check user is admin
        self.login(self.EMAIL_TEST_2)

        with self.app() as client:
            res = client.get('/type/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # type not found
        with self.app() as client:
            res = client.get('/type/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Type not found",json.loads(res.data)['message'])
        # get specific type
        type_model = Type.query.filter_by(name=self.NAME).first()
        with self.app() as client:
            res = client.get('/type/crud/{}'.format(type_model.id),
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)

    def test_06_validation_update_type(self):
        # check user is admin
        self.login(self.EMAIL_TEST_2)

        with self.app() as client:
            res = client.put('/type/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)

        # type not found
        with self.app() as client:
            res = client.put('/type/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Type not found",json.loads(res.data)['message'])

        type_model = Type.query.filter_by(name=self.NAME).first()
        # name, category_id blank
        with self.app() as client:
            res = client.put('/type/crud/{}'.format(type_model.id),json={'name':'','category_id':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['name'])
            self.assertListEqual(["Not a valid integer."],json.loads(res.data)['category_id'])
        # check category_id negative number
        with self.app() as client:
            res = client.put('/type/crud/{}'.format(type_model.id),json={'category_id':-1},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Value must be greater than 0"],json.loads(res.data)['category_id'])
        # category_id not found
        with self.app() as client:
            res = client.put('/type/crud/{}'.format(type_model.id),json={'category_id':99999},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Category not found"],json.loads(res.data)['category_id'])

    def test_07_update_type(self):
        type_model = Type.query.filter_by(name=self.NAME).first()
        category = Category.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.put('/type/crud/{}'.format(type_model.id),json={'name':self.NAME_2,'category_id':category.id},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success update type.",json.loads(res.data)['message'])

    def test_08_create_another_type(self):
        category = Category.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.post('/type/create',json={'name': self.NAME,'category_id':category.id},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add type.",json.loads(res.data)['message'])

    def test_09_name_already_exists_update_type(self):
        type_model = Type.query.filter_by(name=self.NAME_2).first()
        category = Category.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.put('/type/crud/{}'.format(type_model.id),json={'name':self.NAME,'category_id':category.id},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["The name has already been taken."],json.loads(res.data)['name'])

    def test_10_get_all_type(self):
        # check list is not empty & no need login
        with self.app() as client:
            res = client.get('/types')
            self.assertEqual(200,res.status_code)
            self.assertNotEqual([],json.loads(res.data))

    def test_11_validation_delete_type(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.delete('/type/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # type not found
        with self.app() as client:
            res = client.delete('/type/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Type not found",json.loads(res.data)['message'])

    def test_12_delete_type_one(self):
        type_model = Type.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.delete('/type/crud/{}'.format(type_model.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete type.",json.loads(res.data)['message'])

    def test_13_delete_type_two(self):
        type_model = Type.query.filter_by(name=self.NAME_2).first()

        with self.app() as client:
            res = client.delete('/type/crud/{}'.format(type_model.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete type.",json.loads(res.data)['message'])

    def test_98_delete_category(self):
        category = Category.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.delete('/category/crud/{}'.format(category.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete category.",json.loads(res.data)['message'])

    def test_99_delete_user_from_db(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.delete_from_db()
        user = User.query.filter_by(email=self.EMAIL_TEST_2).first()
        user.delete_from_db()
