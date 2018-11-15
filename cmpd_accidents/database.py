"""
Generic database interface for defining connector services
"""
from pymongo import MongoClient
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
        except PyMongoError as e:
            self.logger.exception('PyMongo error: {0}'.format(str(e)))
        except Exception as ex:
            self.logger.exception('Internal Server error: {0}'.format(str(ex)))