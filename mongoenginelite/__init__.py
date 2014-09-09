from mongoengine import Document
import os

from objects import Database
from overrides import new_get_collection, new_get_db
import overrides

_project_root = None
_models_module = None

def connect(db_name):
    global _project_root, _models_module

    _project_root = os.getcwd()
    overrides._db_file_name = db_name
    if '.json' not in db_name:
        db_name = db_name + '.json'

    Database.database_path = os.path.join(_project_root, db_name)
    database = open(Database.database_path, 'w')
    database.close()

    # Override mongoengine _get_db function
    Document._old_get_db = Document._get_db
    Document._get_db = new_get_db

    # Override mongoengine _get_collection function
    Document._old_get_connection = Document._get_collection
    Document._get_collection = new_get_collection