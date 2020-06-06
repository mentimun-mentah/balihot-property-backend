import json
from basetest import BaseTest
from services.models.UserModel import User
from services.models.CategoryModel import Category

class CategoryTest(BaseTest):
    def test_00_add_2_user(self):
        self.register(self.EMAIL_TEST,'asd')
        self.register(self.EMAIL_TEST_2,'asd2')

        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST).first())
        self.assertTrue(User.query.filter_by(email=self.EMAIL_TEST_2).first())

    def test_01_validation_create_category(self):
        self.login(self.EMAIL_TEST_2)
        # can't access without role admin
        with self.app() as client:
            res = client.post('/category/create',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.role = 2
        user.save_to_db()
        # login user 1
        self.login(self.EMAIL_TEST)

        # name blank
        with self.app() as client:
            res = client.post('/category/create',json={'name':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['name'])

    def test_02_create_category(self):
        with self.app() as client:
            res = client.post('/category/create',json={'name':self.NAME},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add category.",json.loads(res.data)['message'])

    def test_03_name_already_taken_create_category(self):
        with self.app() as client:
            res = client.post('/category/create',json={'name':self.NAME},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["The name has already been taken."],json.loads(res.data)['name'])

    def test_04_get_category_by_id(self):
        # check user is admin
        self.login(self.EMAIL_TEST_2)

        with self.app() as client:
            res = client.get('/category/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # category not found
        with self.app() as client:
            res = client.get('/category/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Category not found",json.loads(res.data)['message'])
        # get specific category
        category = Category.query.filter_by(name=self.NAME).first()
        with self.app() as client:
            res = client.get('/category/crud/{}'.format(category.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertIn("id",json.loads(res.data).keys())
            self.assertIn("name",json.loads(res.data).keys())

    def test_05_validation_update_category(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.put('/category/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)

        # category not found
        with self.app() as client:
            res = client.put('/category/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Category not found",json.loads(res.data)['message'])

        # name blank
        category = Category.query.filter_by(name=self.NAME).first()
        with self.app() as client:
            res = client.put('/category/crud/{}'.format(category.id),json={'name':''},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["Length must be between 3 and 100."],json.loads(res.data)['name'])

    def test_06_update_category(self):
        category = Category.query.filter_by(name=self.NAME).first()
        with self.app() as client:
            res = client.put('/category/crud/{}'.format(category.id),json={'name':self.NAME_2},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success update category.",json.loads(res.data)['message'])

    def test_07_create_another_category(self):
        with self.app() as client:
            res = client.post('/category/create',json={'name':self.NAME},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(201,res.status_code)
            self.assertEqual("Success add category.",json.loads(res.data)['message'])

    def test_08_name_already_exists_update_category(self):
        category = Category.query.filter_by(name=self.NAME).first()
        with self.app() as client:
            res = client.put('/category/crud/{}'.format(category.id),json={'name':self.NAME_2},
                headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(400,res.status_code)
            self.assertListEqual(["The name has already been taken."],json.loads(res.data)['name'])

    def test_09_validation_delete_category(self):
        self.login(self.EMAIL_TEST_2)
        # check user is admin
        with self.app() as client:
            res = client.delete('/category/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(403,res.status_code)
            self.assertEqual("Forbidden access this endpoint!",json.loads(res.data)['msg'])

        self.login(self.EMAIL_TEST)
        # region not found
        with self.app() as client:
            res = client.delete('/category/crud/9999',headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(404,res.status_code)
            self.assertEqual("Category not found",json.loads(res.data)['message'])

    def test_10_delete_category_one(self):
        category = Category.query.filter_by(name=self.NAME).first()

        with self.app() as client:
            res = client.delete('/category/crud/{}'.format(category.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete category.",json.loads(res.data)['message'])

    def test_11_delete_category_two(self):
        category = Category.query.filter_by(name=self.NAME_2).first()

        with self.app() as client:
            res = client.delete('/category/crud/{}'.format(category.id),headers={'Authorization':f"Bearer {self.ACCESS_TOKEN}"})
            self.assertEqual(200,res.status_code)
            self.assertEqual("Success delete category.",json.loads(res.data)['message'])

    def test_99_delete_user_from_db(self):
        user = User.query.filter_by(email=self.EMAIL_TEST).first()
        user.delete_from_db()
        user = User.query.filter_by(email=self.EMAIL_TEST_2).first()
        user.delete_from_db()
