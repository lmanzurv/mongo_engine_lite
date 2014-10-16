from pymongo.collection import Collection as PymongoCollection
from pymongo.database import Database as PymongoDatabase
from pymongo.cursor import Cursor as PymongoCursor
from pymongo.common import WriteConcern
from pymongo import read_preferences as rp, helpers
from bson.binary import OLD_UUID_SUBTYPE
from bson.objectid import ObjectId
from bson.json_util import dumps, loads
from bson.son import SON
from collections import deque
import json, uuid, warnings, hashlib

class Collection(PymongoCollection):
    def __init__(self, database, name, create=False, **kwargs):
        super(Collection, self).__init__(database, name, create, **kwargs)
        
    def __call__(self, *args, **kwargs):
        pass
        
    def __getattr__(self, name):
        return Collection(self.__database, u"%s.%s" % (self.__name, name))
        
    def ensure_index(self, key_or_list, cache_for=300, **kwargs):
        return None

    def find(self, *args, **kwargs):
        return Cursor(self, *args, **kwargs)
        
    def find_one(self, spec_or_id=None, *args, **kwargs):
        try:
            cursor = self.find(spec_or_id, *args, **kwargs)
            for result in cursor.limit(-1):
                return result
        except:
            return None

    def insert(self, to_save, manipulate=True, *args, **kwargs):
        if isinstance(to_save, dict):
            to_save = [to_save]

        for obj in to_save:
            if manipulate:
                if '_id' not in obj:
                    obj['_id'] = ObjectId()
        
        ids = self.database.execute(self.name, Database._INSERT, to_save)

        if len(ids) == 1:
            return ids[0]
        else:
            return ids

    def update(self, document, spec, upsert=False, manipulate=False, safe=None, multi=False, check_keys=True, **kwargs):
        response = self.database.execute(self.name, Database._UPDATE, document, spec=spec)
        response['updatedExisting'] = False
        response['n'] = None

        return response

    def remove(self, spec_or_id=None, safe=None, multi=True, **kwargs):
        self.database.execute(self.name, Database._DELETE, None, spec=spec_or_id)

class Cursor(PymongoCursor):
    __id = None
    
    def __init__(self, collection, query, **kwargs):
        super(Cursor, self).__init__(collection, **kwargs)
        self._query = query

    def _refresh(self):
        if len(self.__data) or self.__killed:
            return len(self.__data)

        try:
            db = self.__collection.database
            self.__data = deque(db.execute(self.__collection.name, Database._QUERY, self._query))
            self.__killed = True
        
            return len(self.__data)
        except Exception as e:
            return 0

    def __getitem__(self, index):
        self._refresh()
        if index >= len(self.__data) or index < 0:
            raise Exception('Invalid index')
        return self.__data[index]

class Database(PymongoDatabase):

    _INSERT = 0
    _QUERY = 1
    _UPDATE = 2
    _DELETE = 3
    database_path = None

    def __init__(self, connection, name):
        super(Database, self).__init__(connection, name)
        
    def __call__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return Collection(self, name)
        
    def error(self):
        return None
        
    def command(self, command, value=1,
                check=True, allowable_errors=[],
                uuid_subtype=OLD_UUID_SUBTYPE, compile_re=True, **kwargs):
        cmd = dict()
        if command == 'filemd5':
            cmd.update(root=kwargs['root'], filemd5=value)
                
        return self._execute_command(cmd)
        
    def _execute_command(self, command):
        response = dict()
        
        command = json.loads(dumps(command))
        print 'DATABASE COMMAND', command
        keys = command.keys()
        
        if 'count' in keys:
            result = self.collection.count()
            print 'COUNT RESULT', result
            # TODO finish
        
        elif 'filemd5' in keys:
            collection = '%s.chunks' % command['root']
            file_id = loads(json.dumps(command['filemd5']))
            chunks = list()
            
            n = 0
            chunk = self.execute(collection, Database._QUERY, { 'files_id': file_id, 'n': n })
            while len(chunk) > 0:
                chunks.append(json.loads(dumps(chunk)))
                n += 1
                chunk = self.execute(collection, Database._QUERY, { 'files_id': file_id, 'n': n })
            
            if len(chunks) > 0:
                filemd5 = hashlib.md5(dumps(chunks)).hexdigest()
                response.update(md5=filemd5)
            else:
                raise Exception(u'No chunks found for file with id %s' % file_id)
        
        return response

    def execute(self, collection, operation, content=None, spec=None):
        database = open(self.database_path, 'r')
        db = json.load(database)
        database.close()
        
        response = None
        new_content = None
        if operation == self._INSERT:
            new_content = self.connection.insert(collection, db, content)

            ids = list()
            for obj in content:
                ids.append(obj['_id'])
            response = ids

        elif operation == self._QUERY:
            if collection == '$cmd':
                response = self._execute_command(content)
            else:
                response = self.connection.query(collection, db, content)

        elif operation == self._UPDATE:
            new_content, new_obj = self.connection.update(collection, db, content, spec)
            response = new_obj

        elif operation == self._DELETE:
            new_content = self.connection.delete(collection, db, spec)

        if new_content is not None:
            database = open(self.database_path, 'w')
            database.write(new_content)
            database.close()

        return response

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
        self.document_class = None
        self.is_mongos = True
        self.tz_aware = True
        
    def __getattr__(self, name):
        return Database(self, name)

    def _ensure_connected(self, sync=False):
        pass

    def _filter(self, content, spec):
        for key, value in spec.iteritems():
            if isinstance(value, ObjectId):
                value = json.loads(dumps(ObjectId(oid=value)))

            remove = list()
            for item in content:
                if item[key] != value:
                    remove.append(item)
                    
            content = [it for it in content if it not in remove]
        return content
        
    def start_request(self):
        return self
        
    def end_request(self):
        pass

    def insert(self, collection, database, to_save):
        if database.get(collection) is None:
            database[collection] = list()

        json_to_save = json.loads(dumps(to_save))
        for obj in json_to_save:
            exists = [item for item in database[collection] if item.get('_id') == obj['_id']]
            if len(exists) == 0:
                database[collection].append(obj)
            elif len(exists) > 1:
                raise Exception('There cannot be two elements with the same id')
            else:
                exists[0] = obj

        return json.dumps(database, indent=4)

    def query(self, collection, database, query=None):
        response = list()
        
        col = database.get(collection)

        if col is not None:
            if query:
                subcol = list(col)
                response = loads(json.dumps(self._filter(subcol, query)))
            else:
                response = loads(json.dumps(col))
            
        return response

    def update(self, collection, database, document, spec):
        content = json.loads(dumps(document))
        
        col = database.get(collection)
        if col is not None:
            for doc in col:
                if doc['_id'] == content['_id']:
                    for key, value in spec.iteritems():
                        if key == '$set':
                            for field, fvalue in value.iteritems():
                                if isinstance(fvalue, ObjectId):
                                    fvalue = json.loads(dumps(fvalue))
                                doc[field] = fvalue
                    
                    content = doc
                    break
        else:
            raise Exception('Cannot update a document from an inexistent collection')

        return json.dumps(database, indent=4), loads(json.dumps(content))

    def delete(self, collection, database, spec):
        col = database.get(collection)

        if col is not None:
            subcol = list(col)
            to_delete = self._filter(subcol, spec)
            if to_delete:
                col = [it for it in col if it not in to_delete]
                database[collection] = col
            
        else:
            raise Exception('Cannot delete a document from an inexistent collection')

        return json.dumps(database, indent=4)
