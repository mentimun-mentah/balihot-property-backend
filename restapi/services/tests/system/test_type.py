import json
from basetest import BaseTest

class TypeTest(BaseTest):
    def test_00_get_all_type(self):
        # check list is not empty & no need login
        with self.app() as client:
            res = client.get('/types')
            self.assertEqual(200,res.status_code)
            self.assertNotEqual([],json.loads(res.data))
