from pymongo.collection import Collection as PymongoCollection
from pymongo.database import Database as PymongoDatabase
from pymongo.common import WriteConcern
from bson.binary import OLD_UUID_SUBTYPE
from bson.objectid import ObjectId
import os

class Collection(PymongoCollection):
    def __init__(self, database, name, create=False, **kwargs):
        super(Collection, self).__init__(database, name, create, **kwargs)
        
    def __call__(self, *args, **kwargs):
        pass

    def insert(self, to_save, manipulate=True, *args, **kwargs):
        if isinstance(to_save, dict):
            to_save = [to_save]

        ids = list()

        for obj in to_save:
            if manipulate:
                if '_id' not in obj:
                    obj['_id'] = ObjectId()
                
            ids.append(obj['_id'])
        
        self.database.execute(Database._INSERT, to_save)

        if len(ids) == 1:
            return ids[0]
        else:
            return ids

class Database(PymongoDatabase):

    _INSERT = 'insert'
    database_path = None

    def __init__(self, connection, name):
        super(Database, self).__init__(connection, name)

    def execute(self, operation, content):
        database = open(self.database_path, 'w')
        
        if operation == self._INSERT:
            self.connection.insert(database, content)

        database.close()

class Connection:
    def __init__(self):
        self.slave_okay = True
        self.read_preference = True
        self.tag_sets = None
        self.secondary_acceptable_latency_ms = 1
        self.safe = True
        self.uuid_subtype = OLD_UUID_SUBTYPE
        self.write_concern = WriteConcern()
        self.max_wire_version = 2

    def _ensure_connected(self, sync=False):
        pass

    def insert(self, database, to_save):
        print 'Connection insert: ',to_save