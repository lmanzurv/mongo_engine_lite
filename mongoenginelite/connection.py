from mongoengine.connection import DEFAULT_CONNECTION_NAME
from mongoengine.connection import connect as me_connect
from mongo.connection import Connection
from mongoengine import Document
from mengine.document import _get_collection
import sys, os, mongoengine, traceback

__all__ = ['connect', 'get_connection']

_database_path = None

def _prepare():
    mongoengine.connection.get_connection = get_connection
    #sys.modules['mongoengine.connection'].get_connection = get_connection
    Document._get_collection = _get_collection

def connect(db=None, alias=DEFAULT_CONNECTION_NAME, **kwargs):
    global _database_path
    
    _prepare()
    
    db_file = db
    if '.json' not in db_file:
        db_file = db_file + '.json'
        
    _project_root = os.getcwd()
    _database_path = os.path.join(_project_root, db_file)

    try:
        if os.stat(_database_path).st_size <= 0:
            database = open(_database_path, 'w')
            json.dump(dict(), database, indent=4)
            database.close()
    except OSError:
        database = open(_database_path, 'w')
        json.dump(dict(), database, indent=4)
        database.close()
    
    return me_connect(db, alias)

def get_connection(alias=DEFAULT_CONNECTION_NAME, reconnect=False):
    # Connect to the database if not already connected
    global _database_path
    
    if reconnect:
        disconnect(alias)

    _connections = mongoengine.connection._connections
    _connection_settings = mongoengine.connection._connection_settings
    if alias not in _connections:
        if alias not in _connection_settings:
            raise Exception('You are attempting to connect to an inexistent database')
        conn_settings = _connection_settings[alias].copy()

        conn_settings.pop('name', None)
        conn_settings.pop('username', None)
        conn_settings.pop('password', None)
        conn_settings.pop('authentication_source', None)

        connection_class = Connection
        try:
            connection = None
            # check for shared connections
            connection_settings_iterator = ((db_alias, settings.copy()) for db_alias, settings in _connection_settings.iteritems())
            for db_alias, connection_settings in connection_settings_iterator:
                connection_settings.pop('name', None)
                connection_settings.pop('username', None)
                connection_settings.pop('password', None)
                if conn_settings == connection_settings and _connections.get(db_alias, None):
                    connection = _connections[db_alias]
                    break
            
            _connections[alias] = connection if connection else connection_class(_database_path, **conn_settings)
        except Exception, e:
            print 'GET CONNECTION ERROR',e
            ex_type, ex, tb = sys.exc_info()
            traceback.print_tb(tb)
            raise Exception('Cannot establish connection to database')
    return _connections[alias]
