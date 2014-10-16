from mongoengine import Document
import os, sys, mongoengine.connection
from mongoengine.connection import DEFAULT_CONNECTION_NAME

from objects import Database
from overloads import new_get_collection, new_get_db, new_get_connection
import overloads, json

_project_root = None
_models_module = None

def connect(db_name):
    global _project_root, _models_module

    _project_root = os.getcwd()
    overloads._db_file_name = db_name
    
    sys.modules['mongoengine.connection'].DEFAULT_CONNECTION_NAME = db_name
    sys.modules['mongoengine.connection'].get_connection = new_get_connection
    
    mongoengine.connection._connection_settings[DEFAULT_CONNECTION_NAME] = dict(name=db_name, username=None, password=None)

    if '.json' not in db_name:
        db_name = db_name + '.json'

    Database.database_path = os.path.join(_project_root, db_name)

    try:
        if os.stat(Database.database_path).st_size <= 0:
            database = open(Database.database_path, 'w')
            json.dump(dict(), database, indent=4)
            database.close()
    except OSError:
        database = open(Database.database_path, 'w')
        json.dump(dict(), database, indent=4)
        database.close()

    # Override mongoengine _get_db function
    Document._get_db = new_get_db

    # Override mongoengine _get_collection function
    Document._get_collection = new_get_collection
    
    return new_get_connection()
