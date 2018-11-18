from unittest import TestCase
from unittest.mock import patch
import cmpd_accidents
import shutil

class TestDatabase(TestCase):
    """ Database integration tests """
    @patch('cmpd_accidents.MongoDBConnect')
    def test_mongo_sanity_check(self, mock_db):
        mock_db.return_value.insert_bulk.return_value = None
        inst = cmpd_accidents.MongoDBConnect("localhost", 27017, "accidents")
        result = inst.insert_bulk(items=[{"x_coord":"1432859","event_no":"S1115184904","y_coord":"514899","datetime_add":"2018-11-15T18:49:43","event_desc":"VEHICLE DISABLED IN ROADWAY","address":"NATIONS FORD RD & CHOYCE AV","latitude":"35.149888","division":"STEELE CREEK","longitude":"-80.897438","event_type":"VE-DIS/R"}, {"x_coord":"1440308","event_no":"S1115184802","y_coord":"546294","datetime_add":"2018-11-15T18:48:31","event_desc":"ACCIDENT-PERSONAL INJURY","address":"BERRYHILL RD & TUCKASEEGEE RD","latitude":"35.236524","division":"METRO","longitude":"-80.874506","event_type":"AC-PI"}])
        inst.insert_bulk.assert_called()
        inst.insert_bulk.assert_called_with(items=[{"x_coord":"1432859","event_no":"S1115184904","y_coord":"514899","datetime_add":"2018-11-15T18:49:43","event_desc":"VEHICLE DISABLED IN ROADWAY","address":"NATIONS FORD RD & CHOYCE AV","latitude":"35.149888","division":"STEELE CREEK","longitude":"-80.897438","event_type":"VE-DIS/R"}, {"x_coord":"1440308","event_no":"S1115184802","y_coord":"546294","datetime_add":"2018-11-15T18:48:31","event_desc":"ACCIDENT-PERSONAL INJURY","address":"BERRYHILL RD & TUCKASEEGEE RD","latitude":"35.236524","division":"METRO","longitude":"-80.874506","event_type":"AC-PI"}])
        self.assertEqual(result, None)

    def test_mongo_init(self):
        mock_db = cmpd_accidents.MongoDBConnect()
        self.assertTrue(type(mock_db) == cmpd_accidents.MongoDBConnect)
        self.assertTrue(hasattr(mock_db, '__init__'))
        self.assertTrue(hasattr(mock_db, '__enter__'))
        self.assertTrue(hasattr(mock_db, '__exit__'))
        self.assertTrue(hasattr(mock_db, '__init__'))
        self.assertTrue(hasattr(mock_db, 'insert_bulk'))

    def test_mongo_attributes(self):
        mock_db = cmpd_accidents.MongoDBConnect('localhost', 8888, 'accidents')
        self.assertTrue(hasattr(mock_db, 'connection'))
        self.assertTrue(hasattr(mock_db, 'host'))
        self.assertTrue(hasattr(mock_db, 'port'))
        self.assertTrue(hasattr(mock_db, 'collection_name'))
        self.assertTrue(hasattr(mock_db, 'collection'))
        self.assertTrue(mock_db.host == 'localhost')
        self.assertTrue(mock_db.port == 8888)
        self.assertTrue(mock_db.collection_name == 'accidents')
        mock_db.__enter__()
        self.assertTrue('accidents' in str(mock_db.collection))
        self.assertTrue('localhost:8888' in str(mock_db.collection))
        mock_db.__exit__(None, None, None)

    def test_mysql_init(self):
        mock_db = cmpd_accidents.SQLAlchemyConnect('mysql+pymysql://root:root@localhost:3306/db')
        self.assertTrue(type(mock_db) == cmpd_accidents.SQLAlchemyConnect)
        self.assertTrue(hasattr(mock_db, '__init__'))
        self.assertTrue(hasattr(mock_db, '__enter__'))
        self.assertTrue(hasattr(mock_db, '__exit__'))
        self.assertTrue(hasattr(mock_db, '__init__'))
        self.assertTrue(hasattr(mock_db, 'insert_bulk'))

    def test_mysql_attributes(self):
        mock_db = cmpd_accidents.SQLAlchemyConnect('mysql+pymysql://root:root@localhost:3306/db')
        self.assertTrue(hasattr(mock_db, 'connection_string'))
        self.assertTrue(mock_db.connection_string == 'mysql+pymysql://root:root@localhost:3306/db')
        mock_db.__enter__()
        self.assertTrue(hasattr(mock_db, 'engine'))
        self.assertTrue(hasattr(mock_db, 'session'))
        mock_db.__exit__(None, None, None)

    @classmethod
    def tearDownClass(self):
        """ Tear down """
        shutil.rmtree('./log')