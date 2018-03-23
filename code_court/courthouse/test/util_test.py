import util
from base_test import BaseTest
import model
import json

class UtilTestCase(BaseTest):
    """
    Contains tests for the util functions
    """

    def test_add_versions(self):
        """test the add_versions function"""

        LANG_VER = '{"java": "1.1.1", "c": "2.2.2", "python": "3.3.3"}'

        util.add_versions(LANG_VER)

        lang_list = json.loads(LANG_VER)

        for lang in lang_list:
            results = model.Language.query.filter_by(name=lang).scalar()
            #self.assertEqual(len(results), LANG_VER[lang])
            self.assertIsNotNone(results.version)
