"""
Generic database interface for defining connector services
PyMongo is used for MongoDB related persistence
SQLAlchemy is used for relational db type persistence
"""
from pymongo import MongoClient # pymongo
from sqlalchemy import create_engine # sqlalchemy
from sqlalchemy.orm import sessionmaker # sqlalchemy
from sqlalchemy import MetaData # sqlalchemy
from sqlalchemy import Table #sqlalchemy
from urllib.parse import urlparse
from cmpd_accidents import Logger

class MongoDBConnect(object):
    """
    The Mongo database connector
    Args:
        host: host to connect, if empty default to localhost
        port: port to connect, if empty default to mongodb port
        collection: the collection to use
    """
    def __init__(self, host='localhost', port=27017, collection_name='accidents'):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.collection = None
        self.connection = None
        self.logger = Logger('log', self.__class__.__name__, maxbytes=10 * 1024 * 1024).get()

    def __enter__(self):
        self.connection = MongoClient(self.host, self.port)
        self.collection = self.connection[urlparse(self.host).path[1:]][self.collection_name]
        self.logger.info('Mongo connection created: {0}'.format(self.connection))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def insert_bulk(self, items):
        """
        MongoDB bulk insert
        Args:
           items: list of json to insert
        """
        try:
            self.collection.insert(items)
            self.logger.info('Successfully inserted items: {0}'.format(str(items)))
        except Exception as e:
            self.logger.exception('PyMongo database error: {0}'.format(str(e)))
            raise e

class SQLAlchemyConnect(object):
    """
    SQLAlchemy/MySQL connector
    Args:
        connection_string: The database connection string
    """
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.session = None
        self.logger = Logger('log', self.__class__.__name__, maxbytes=10 * 1024 * 1024).get()

    def __enter__(self):
        self.engine = create_engine(self.connection_string)
        Session = sessionmaker()
        self.session = Session(bind=self.engine)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def insert_bulk(self, table, items):
        """
        SQLAlchemy bulk insert
        Args:
            items: list of json to insert
            table: table to insert data
        """
        try:
            metadata = MetaData(bind=self.engine, reflect=True)
            active_table = Table(table, metadata, autoload=True, autoload_with=self.engine)
            self.session.execute(active_table.insert(), items)
            self.session.commit() # commit transaction
            self.logger.info('Successfully inserted items: {0} into table: {1}'.format(str(items), active_table))
        except Exception as e:
            self.logger.exception('SQLAlchemy database error: {0}'.format(str(e)))
            raise e