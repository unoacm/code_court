import util
from base_test import BaseTest
import model
import json
import bcrypt
from database import db_session
import datetime
from flask import request

class UtilTestCase(BaseTest):
    """
    Contains tests for the util functions
    """

    def test_hash_password(self):
         """test the hash_password function"""
        
         password = "password"
         hashed_password = util.hash_password(password)
         self.assertEqual(bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")), True)

    def test_is_password_matching(self):
        """test the is_password_matching function"""
        
        password = "8wpyathgors"
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self.assertEqual(util.is_password_matching(password, hashed_password.decode("utf-8")), True)

    def test_checkbox_result_to_bool(self):
         """test the checkbox_result_to_bool function"""

         self.assertEqual(util.checkbox_result_to_bool("on"), True)
         self.assertEqual(util.checkbox_result_to_bool("off"), False)
        
    def test_get_configuration(self):
        """test the get_configuration function""" 

        string_config = model.Configuration("String_Config", "sample", "string", "admin")
        bool_config = model.Configuration("Bool_Config", "True", "bool", "admin")
        integer_config = model.Configuration("Integer_Config", "12", "integer", "admin")
        
        db_session.add_all([string_config, bool_config, integer_config])
        db_session.commit()

        self.assertEqual(util.get_configuration("String_Config"), "sample")
        self.assertEqual(util.get_configuration("Bool_Config"), True)
        self.assertEqual(util.get_configuration("Integer_Config"), 12)        

    def test_i(self):
        """test the i function"""
         
        x = "12"
        value = util.i(x)
        self.assertEqual(int(x), value)

    def test_str_to_dt(self):
        """test the str_to_dt function"""
    
        time = "2018-03-29T03:47:42Z"
        dt = util.str_to_dt(time)

        self.assertEqual(dt, datetime.datetime(2018, 3, 29, 3, 47, 42))

    def test_strs_to_dt(self):
        """test the strs_to_dt function"""

        date_string = "2018-03-29"
        time_string = "04:49:59"
        dt = util.strs_to_dt(date_string, time_string)
         
        self.assertEqual(dt, datetime.datetime(2018, 3, 29, 4, 49, 59))    

    def test_time_str_to_dt(self):
        """tests the time_str_to_dt function"""

        time = "04:53:10"
        dt = util.time_str_to_dt(time)
        
        #The default value from datetime.strptime for the year is 1900
        self.assertEqual(dt, datetime.datetime(1900, 1, 1, 4, 53, 10))

    def test_dt_to_str(self):
        """tests the dt_to_str function"""

        dt = datetime.datetime(2018, 4, 2, 9, 20, 46)

        self.assertEqual(util.dt_to_str(dt), "2018-04-02T09:20:46Z")

    def test_dt_to_date_str(self):
        """tests the dt_to_date_str function"""

        dt = datetime.datetime(2018, 4, 2, 9, 21, 56)

        self.assertEqual(util.dt_to_date_str(dt), "2018-04-02")

    def test_dt_to_time_str(self):    
        """tests the dt_to_time_str function """

        dt = datetime.datetime(2018, 4, 2, 9, 23, 39)

        self.assertEqual(util.dt_to_time_str(dt), "09:23:39")

    def test_add_versions(self):
        """test the add_versions function"""

        LANG_VER = '{"java": "1.1.1", "c": "2.2.2", "python": "3.3.3"}'

        util.add_versions(LANG_VER)

        lang_list = json.loads(LANG_VER)

        for lang in lang_list:
            results = model.Language.query.filter_by(name=lang).scalar()
            self.assertIsNotNone(results.version)
