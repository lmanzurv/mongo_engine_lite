from mongoengine import Document
import os

from objects import Database
from overloads import new_get_collection, new_get_db
import overloads, json

_project_root = None
_models_module = None

def connect(db_name):
    global _project_root, _models_module

    _project_root = os.getcwd()
    overloads._db_file_name = db_name
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