from pymongo.collection import Collection as PymongoCollection
from bson.objectid import ObjectId
from cursor import Cursor
from mongoenginelite import settings

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
        
        ids = self.database.execute(self.name, settings._INSERT, to_save)

        if len(ids) == 1:
            return ids[0]
        else:
            return ids
            
    def update(self, document, spec, upsert=False, manipulate=False, safe=None, multi=False, check_keys=True, **kwargs):
        response = self.database.execute(self.name, settings._UPDATE, document, spec=spec)
        response['updatedExisting'] = False
        response['n'] = None

        return response

    def remove(self, spec_or_id=None, safe=None, multi=True, **kwargs):
        self.database.execute(self.name, settings._DELETE, None, spec=spec_or_id)
