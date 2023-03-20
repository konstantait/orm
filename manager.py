from database import Database
from logger import child_logger

logger = child_logger('manager')


class Manager(object):

    def __init__(self, model):
        self._database = None
        self._model = model

    def __get__(self, instance, owner):
        if instance is not None:
            raise AttributeError(f"Manager isn't accessible via {owner.__name__} instances.")
        return self

    @property
    def backend(self):
        return self._database

    @backend.setter
    def backend(self, database):
        if not isinstance(database, Database):
            raise ValueError(f'{database} is not a Database object.')
        self._database = database

    # manage table

    def table_exists(self):
        sql = f'''
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='{self._model.__table__}';'''
        result = self._database.select(sql)
        return True if len(result) == 1 else False

    def create_table(self):
        sql = f'''
        CREATE TABLE IF NOT EXISTS {self._model.__table__} (
            {self._model.__primary_key__} INTEGER PRIMARY KEY AUTOINCREMENT,
            {',            '.join(self._model.__columns__)});'''
        # {',\n            '.join(self._model.__columns__)});'''
        return self._database.execute(sql)

    def drop_table(self):
        sql = f'''
        DROP TABLE IF EXISTS {self._model.__table__};'''
        return self._database.execute(sql, autocommit=False)

    # retrieve data

    def all(self):
        sql = f'''
        SELECT * FROM {self._model.__table__};'''
        results = self._database.select(sql)
        return [self._model(dict(r)) for r in results]

    def find(self, filter=None, order_by=None):
        sql = f'''
        SELECT * FROM {self._model.__table__}'''
        if filter is not None:
            sql += f'\n        WHERE {filter}'
        if order_by is not None:
            sql += f'\n        ORDER BY {order_by}'
        sql += ';'
        results = self._database.select(sql)
        return [self._model(dict(r)) for r in results]

    def get(self, pk):
        sql = f'''
        SELECT * FROM {self._model.__table__}
        WHERE {self._model.__primary_key__} = ?;'''
        args = [pk]
        result = self._database.select(sql, *args)
        if len(result) == 1:
            return self._model(dict(result[0]))
        return None

    def exists(self, pk):
        obj = self.get(pk)
        return False if obj is None else True

    def aggregate(self, expression, filter=None):
        sql = f'''
        SELECT {expression} FROM {self._model.__table__}'''
        if filter is not None:
            sql += '\n        WHERE {}'.format(filter)
        sql += ';'
        result = self._database.select(sql)
        if len(result) == 1:
            return dict(result[0])
        return None

    # modify data

    def add(self, obj):
        if self._model.__primary_key__ in obj:
            if self.exists(obj[self._model.__primary_key__]):
                return -1
            sql = f'''
            INSERT INTO {self._model.__table__} ({', '.join([self._model.__primary_key__] + self._model.__fields__)})
            VALUES ({', '.join(['?'] + self._model.__placeholders__)});'''
        else:
            sql = f'''
            INSERT INTO {self._model.__table__} ({', '.join(self._model.__fields__)})
            VALUES ({', '.join(self._model.__placeholders__)});'''
        args = list(obj.values())
        return self._database.execute(sql, *args)

    def update(self, obj):
        sql = f'''
        UPDATE {self._model.__table__}
        SET {', '.join([f + ' = ?' for f in self._model.__fields__])}
        WHERE {self._model.__primary_key__} = ?;'''
        if (self._model.__primary_key__ not in obj) \
                or (not self.exists(obj[self._model.__primary_key__])):
            return -1
        copy = obj.copy()
        pk = copy.pop(self._model.__primary_key__)
        args = list(copy.values()) + [pk]
        return self._database.execute(sql, *args)

    def remove(self, obj):
        sql = '''
        DELETE FROM {self._model.__table__}
        WHERE {self._model.__primary_key__} = ?;'''
        if (self._model.__primary_key__ not in obj) \
                or (not self.exists(obj[self._model.__primary_key__])):
            return -1
        args = [obj[self._model.__primary_key__]]
        return self._database.execute(sql, *args)

    def clear(self):
        sql = f'''
        DELETE FROM {self._model.__table__};'''
        return self._database.execute(sql, autocommit=False)


class classonlymethod(classmethod):

    def __get__(self, instance, cls=None):
        if instance is not None:
            raise AttributeError("Manager isn't accessible via {} instances.".format(cls.__name__))
        return super().__get__(instance, cls)
