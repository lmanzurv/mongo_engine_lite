__all__ = ['_get_collection']

@classmethod
def _get_collection(cls):
    if not hasattr(cls, '_collection') or cls._collection is None:
        db = cls._get_db()
            
        collection_name = cls._get_collection_name()
        if collection_name in db.collection_names():
            cls._collection = db[collection_name]
        else:
            cls._collection = db.create_collection(collection_name)
    
    return cls._collection
