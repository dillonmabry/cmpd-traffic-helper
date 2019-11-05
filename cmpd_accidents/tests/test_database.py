from unittest import TestCase
from unittest.mock import patch
import cmpd_accidents


class TestDatabase(TestCase):
    """ Database integration tests """
    @patch('cmpd_accidents.MongoDBConnect')
    def test_mongo_sanity_check(self, mock_db):
        mock_db.return_value.insert_bulk.return_value = None
        inst = cmpd_accidents.MongoDBConnect("localhost")
        self.assertTrue(hasattr(inst.insert_bulk, "collection"))
        self.assertTrue(mock_db is cmpd_accidents.MongoDBConnect)

    def test_mongo_init(self):
        mock_db = cmpd_accidents.MongoDBConnect("localhost")
        self.assertTrue(type(mock_db) == cmpd_accidents.MongoDBConnect)
        self.assertTrue(hasattr(mock_db, '__init__'))
        self.assertTrue(hasattr(mock_db, '__enter__'))
        self.assertTrue(hasattr(mock_db, '__exit__'))
        self.assertTrue(hasattr(mock_db, '__init__'))
        self.assertTrue(hasattr(mock_db, 'insert_bulk'))

    def test_mongo_attributes(self):
        mock_db = cmpd_accidents.MongoDBConnect('localhost')
        self.assertTrue(hasattr(mock_db, 'connection'))
        self.assertTrue(hasattr(mock_db, 'host'))
        self.assertTrue(mock_db.host == 'localhost')
        mock_db.__enter__()
        mock_db.__exit__(None, None, None)

    def test_mysql_init(self):
        mock_db = cmpd_accidents.SQLAlchemyConnect(
            'mysql+pymysql://root:root@localhost:3306/db')
        self.assertTrue(type(mock_db) == cmpd_accidents.SQLAlchemyConnect)
        self.assertTrue(hasattr(mock_db, '__init__'))
        self.assertTrue(hasattr(mock_db, '__enter__'))
        self.assertTrue(hasattr(mock_db, '__exit__'))
        self.assertTrue(hasattr(mock_db, '__init__'))
        self.assertTrue(hasattr(mock_db, 'insert_bulk'))

    def test_mysql_attributes(self):
        mock_db = cmpd_accidents.SQLAlchemyConnect(
            'mysql+pymysql://root:root@localhost:3306/db')
        self.assertTrue(hasattr(mock_db, 'connection_string'))
        self.assertTrue(mock_db.connection_string ==
                        'mysql+pymysql://root:root@localhost:3306/db')
        mock_db.__enter__()
        self.assertTrue(hasattr(mock_db, 'engine'))
        self.assertTrue(hasattr(mock_db, 'session'))
        mock_db.__exit__(None, None, None)
