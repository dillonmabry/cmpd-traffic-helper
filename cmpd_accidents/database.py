"""
Generic database interface for defining connector services
PyMongo is used for MongoDB related persistence
SQLAlchemy is used for relational db type persistence
"""
from pymongo import MongoClient  # pymongo
from sqlalchemy import create_engine  # sqlalchemy
from sqlalchemy.orm import sessionmaker  # sqlalchemy
from sqlalchemy import MetaData  # sqlalchemy
from sqlalchemy import Table  # sqlalchemy
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

    def __init__(self, host='localhost', port=27017):
        self.host = host
        self.port = port
        self.connection = None
        self.logger = Logger('log', self.__class__.__name__,
                             maxbytes=10 * 1024 * 1024).get()

    def __enter__(self):
        self.connection = MongoClient(self.host, self.port)
        self.logger.info(
            'Mongo connection created: {0}'.format(self.connection))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()

    def find_ids(self, collection, ids, cursor_limit):
        """
        Find collection items ids based on search of existing ids
        Args:
            collection: the collection to search
            ids: the existing ids to find in collection
            cursor_limit: the cursor limit of the find
        """
        try:
            exist_events = []
            collection = self.connection[urlparse(
                self.host).path[1:]][collection]
            cursor = collection.find({'event_no': {'$in': ids}}, {
                                     'event_no': 1}).limit(cursor_limit)
            for doc in cursor:
                if doc.get('event_no'):
                    exist_events.append(doc.get('event_no'))
            return exist_events
        except Exception as e:
            self.logger.exception('PyMongo database error: {0}'.format(str(e)))
            raise e

    def insert_bulk(self, collection, items):
        """
        MongoDB bulk insert
        Args:
            collection: the collection to insert to
            items: list of json to insert
        """
        try:
            collection = self.connection[urlparse(
                self.host).path[1:]][collection]
            collection.insert(items)
            self.logger.info(
                'Successfully inserted items: {0}'.format(str(items)))
        except Exception as e:
            self.logger.exception('PyMongo database error: {0}'.format(str(e)))
            raise e

    def get_all(self, collection, limit, order=1):
        """
        MongoDB get all items
        Args:
            collection: collection to get from
            limit: integer of limit of items to retrieve, ie, 1000, 2000, etc.
            order: datetime sort: asc 1, desc -1
        """
        try:
            collection = self.connection[urlparse(
                self.host).path[1:]][collection]
            items = collection.find().sort('datetime_add', order).limit(limit)  # oldest
            self.logger.info(
                'Successfully found items based on limit: {0}'.format(str(limit)))
            return items
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
        self.logger = Logger('log', self.__class__.__name__,
                             maxbytes=10 * 1024 * 1024).get()

    def __enter__(self):
        self.engine = create_engine(self.connection_string)
        Session = sessionmaker()
        self.session = Session(bind=self.engine)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def find_ids(self, table, ids, cursor_limit):
        """
        SQLAlchemy find rows by ids
        Args:
            table: the table to search
            ids: the existing ids to find in table specified
            cursor_limit: the cursor limit of the find
        """
        try:
            metadata = MetaData(bind=self.engine, reflect=True)
            active_table = Table(
                table, metadata, autoload=True, autoload_with=self.engine)
            cursor_results = self.session.execute("""
                SELECT DISTINCT event_no FROM {0};
                """.format(active_table))
            exist_events = []
            for row in cursor_results:
                exist_events.append(row['event_no'])
            return exist_events
        except Exception as e:
            self.logger.exception(
                'SQLAlchemy database error: {0}'.format(str(e)))
            raise e

    def insert_bulk(self, table, items):
        """
        SQLAlchemy bulk insert
        Args:
            table: table to insert data
            items: list of json to insert
        """
        try:
            metadata = MetaData(bind=self.engine, reflect=True)
            active_table = Table(
                table, metadata, autoload=True, autoload_with=self.engine)
            self.session.execute(active_table.insert(), items)
            self.session.commit()  # commit transaction
            self.logger.info('Successfully inserted items: {0} into table: {1}'.format(
                str(items), active_table))
        except Exception as e:
            self.logger.exception(
                'SQLAlchemy database error: {0}'.format(str(e)))
            raise e

    def get_all(self, table):
        """
        SQLAlchemy get all items
        Args:
            table: table to get from
        """
        try:
            metadata = MetaData(bind=self.engine, reflect=True)
            active_table = Table(
                table, metadata, autoload=True, autoload_with=self.engine)
            items = self.session.query(active_table).all()
            self.logger.info('Successfully retrieved selected items: {0} from table: {1}'.format(
                str(items), active_table))
            return items
        except Exception as e:
            self.logger.exception(
                'SQLAlchemy database error: {0}'.format(str(e)))
            raise e
