from objects import Collection, Database, Connection

_db_file_name = None

def new_get_connection(alias=_db_file_name, reconnect=False):
    return Connection()

@classmethod
def new_get_collection(doc_cls):
    if not hasattr(doc_cls, '_collection') or doc_cls._collection is None:
        conn = Connection()
        db = Database(conn, _db_file_name)
        col = Collection(db, doc_cls._get_collection_name())
        doc_cls._collection = col
    return doc_cls._collection

@classmethod
def new_get_db(doc_cls):
    db = None
    if hasattr(doc_cls, '_collection') and doc_cls._collection is not None:
        db = doc_cls._collection.__database
    return db
