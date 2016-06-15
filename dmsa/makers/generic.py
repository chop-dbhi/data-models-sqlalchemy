from __future__ import unicode_literals


class GenericMaker(object):
    """A generic base class for creating SQLAlchemy model classes and DDL
    output.
    """

    name = ''               # A place to store the name of the model.
    fields = []             # A place to store field references.
    model_func = None       # The model class constructor function.
    model_readable = ''     # Readable name of the model class for messages.
    create_ddl_func = None  # The create DDL compilable constructor function.
    drop_ddl_func = None    # The drop DDL compilable constructor function.

    def __init__(self, name, fields):
        """Translate and store the input on the class instance.
        """
        self.name = name
        if isinstance(fields, (list, tuple)):
            self.fields = fields
        elif isinstance(fields, str):
            self.fields = [fields]

    def verify(self):
        """Verify that there is enough information on the class instance to
        create a model and error if there is not.
        """
        if not self.name:
            raise RuntimeError('will not create a %s without an explicit name'.\
                               format(self.model_readable))
        if not self.fields:
            raise RuntimeError('cannot create a %s without field references'.\
                               format(self.model_readable))

    def model_args(self):
        """Prepare a list of arguments for model construction.
        """
        return self.fields

    def model_kwargs(self):
        """Prepare a dictionary of keyword arguments for model construction.
        """
        return {name: self.name}

    def model(self):
        """Construct the model.
        """
        self.verify()
        return self.model_func(*self.model_args(), **self.model_kwargs())

    def create_ddl(self, engine):
        """Output creation DDL.
        """
        return str(self.create_ddl_func(self.model()).compile(
            dialect=engine.dialect)).strip()

    def drop_ddl(self, engine):
        """Output drop DDL.
        """
        return str(self.drop_ddl_func(self.model()).compile(
            dialect=engine.dialect)).strip()
