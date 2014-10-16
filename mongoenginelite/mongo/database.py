from pymongo.database import Database as PymongoDatabase
from bson.binary import OLD_UUID_SUBTYPE
from collection import Collection
from mongoenginelite import settings
from bson.json_util import dumps, loads
import json, hashlib

class Database(PymongoDatabase):
    database_path = None
    
    def __init__(self, connection, name, database_path):
        super(Database, self).__init__(connection, name)
        self.database_path = database_path
        
    def __call__(self, *args, **kwargs):
        pass

    def __getattr__(self, name):
        return Collection(self, name)
        
    def error(self):
        return None

    def collection_names(self):
        database = open(self.database_path, 'r')
        db = json.load(database)
        database.close()
        
        collection_names = list()
        for key, value in db.iteritems():
            collection_names.append(key)
            
        return collection_names
        
    def create_collection(name):
        if name in self.collection_names():
            raise CollectionInvalid('The collection you are attempting to create already exists')
        
        return Collection(self, name)
        
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
            try:
                result = self.collection.count()
                print 'COUNT RESULT', result
            except Exception as e:
                print 'COUNT ERROR', e
            # TODO finish
        
        elif 'filemd5' in keys:
            collection = '%s.chunks' % command['root']
            file_id = loads(json.dumps(command['filemd5']))
            chunks = list()
            
            n = 0
            chunk = self.execute(collection, settings._QUERY, { 'files_id': file_id, 'n': n })
            while len(chunk) > 0:
                chunks.append(json.loads(dumps(chunk)))
                n += 1
                chunk = self.execute(collection, settings._QUERY, { 'files_id': file_id, 'n': n })
            
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
        if operation == settings._INSERT:
            new_content = self.connection.insert(collection, db, content)

            ids = list()
            for obj in content:
                ids.append(obj['_id'])
            response = ids

        elif operation == settings._QUERY:
            if collection == '$cmd':
                response = self._execute_command(content)
            else:
                response = self.connection.query(collection, db, content)

        elif operation == settings._UPDATE:
            new_content, new_obj = self.connection.update(collection, db, content, spec)
            response = new_obj

        elif operation == settings._DELETE:
            new_content = self.connection.delete(collection, db, spec)

        if new_content is not None:
            database = open(self.database_path, 'w')
            database.write(new_content)
            database.close()

        return response
