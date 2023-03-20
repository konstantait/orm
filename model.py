from manager import Manager, classonlymethod
from logger import child_logger

logger = child_logger('model')


class Field(object):

    def __init__(self, name, type, default, primary_key):
        self.name = name
        self.type = type
        self.default = default
        self.primary_key = primary_key


class StringField(Field):

    def __init__(self, name=None, default=''):
        super().__init__(name, 'TEXT', default, False)


class IntegerField(Field):

    def __init__(self, name=None, default=0, primary_key=False):
        super().__init__(name, 'INTEGER', default, primary_key)


class FloatField(Field):

    def __init__(self, name=None, default=0.0):
        super().__init__(name, 'REAL', default, False)


class ModelMetaclass(type):
    logger.info('Metaclass body')

    def __new__(mcs, name, bases, attrs):
        logger.info(f'Metaclass new for {name}')

        if name == 'Model':
            return super().__new__(mcs, name, bases, attrs)

        table = attrs.get('__table__', None) or name.lower()
        mappings = dict()
        primary_key = None
        fields = list()
        columns = list()

        for attr_name, attr_value in attrs.items():
            if isinstance(attr_value, Field):
                mappings[attr_name] = attr_value
                if attr_value.primary_key:
                    if primary_key is not None:
                        raise RuntimeError(f'Duplicate primary key for field: {attr_name}')
                    primary_key = attr_name
                else:
                    fields.append(attr_name)
                    columns.append(f'{attr_name} {attr_value.type}')

        if primary_key is None:
            raise RuntimeError('Primary key not found.')

        for attr_name in mappings.keys():
            attrs.pop(attr_name)

        attrs['__table__'] = table
        attrs['__mappings__'] = mappings
        attrs['__primary_key__'] = primary_key
        attrs['__fields__'] = fields
        attrs['__columns__'] = columns
        attrs['__placeholders__'] = ['?' for _ in range(len(fields))]

        return super().__new__(mcs, name, bases, attrs)

    def __init__(cls, name, bases, attrs):
        logger.info(f'Metaclass init for {name}')
        if name != 'Model':
            cls.objects = Manager(cls)
        super().__init__(name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):
    logger.info('Model body')

    def __init__(self, *args, **kwargs):
        logger.info('Model init')
        for arg in args:
            logger.info(f'*argv: {arg}')
        for key, value in kwargs.items():
            logger.info(f'{key} = {value}')
        super().__init__(*args, **kwargs)

    @classonlymethod
    def exists(cls):
        return cls.objects.table_exists()

    @classonlymethod
    def create(cls):
        return cls.objects.create_table()

    @classonlymethod
    def drop(cls):
        return cls.objects.drop_table()

    def save(self):
        if not self.__class__.exists():
            self.__class__.create()
        return self.__class__.objects.add(self)

    def update(self):
        return self.__class__.objects.update(self)

    def delete(self):
        return self.__class__.objects.remove(self)
