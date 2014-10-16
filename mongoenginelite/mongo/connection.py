from bson.binary import OLD_UUID_SUBTYPE
from pymongo.common import WriteConcern
from database import Database
from bson.json_util import dumps, loads
from bson.objectid import ObjectId
import json

class Connection():
    database_path = None
    
    def __init__(self, database_path, tz_aware=False, **kwargs):
        self.slave_okay = True
        self.read_preference = True
        self.tag_sets = None
        self.secondary_acceptable_latency_ms = 1
        self.safe = True
        self.uuid_subtype = OLD_UUID_SUBTYPE
        self.write_concern = WriteConcern()
        self.document_class = None
        self.max_wire_version = 2
        self.__tz_aware = tz_aware
        self.database_path = database_path

    def __getitem__(self, name):
        return self.__getattr__(name)

    def __getattr__(self, name):
        return Database(self, name, self.database_path)
        
    def __repr__(self):
        return self.database_path
        
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
