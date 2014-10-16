from pymongo.cursor import Cursor as PymongoCursor
from collections import deque
from mongoenginelite import settings

class Cursor(PymongoCursor):
    def __init__(self, collection, query, **kwargs):
        super(Cursor, self).__init__(collection, **kwargs)
        self._query = query

    def _refresh(self):
        if len(self.__data) or self.__killed:
            return len(self.__data)

        try:
            db = self.__collection.database
            self.__data = deque(db.execute(self.__collection.name, settings._QUERY, self._query))
            self.__killed = True
        
            return len(self.__data)
        except:
            return 0
            
    def __getitem__(self, index):
        self._refresh()
        if index >= len(self.__data) or index < 0:
            raise Exception('Invalid index')
        return self.__data[index]
