from __future__ import unicode_literals
from sqlalchemy.schema import Index, CreateIndex, DropIndex
from dmsa.makers.generic import GenericMaker


class IndexMaker(GenericMaker):
    """A class that converts index descriptions into SQLAlchemy model Index
    classes and outputs DDL.
    """

    model_func = Index
    model_readable = 'index'
    create_ddl_func = CreateIndex
    drop_ddl_func = DropIndex

    def model_args(self):
        return [self.name, *self.fields]

    def model_kwargs(self):
        return {}

    def log_ddl(self, engine):
        self.verify()
        if engine.dialect.startswith('oracle'):
            return 'ALTER INDEX %s LOGGING;'.format(self.name)
        raise RuntimeError('cannot log index on non-Oracle backend')

    def unlog_ddl(self, engine):
        self.verify()
        if engine.dialect.startswith('oracle'):
            return 'ALTER INDEX %s NOLOGGING;'.format(self.name)
        raise RuntimeError('cannot unlog index on non-Oracle backend')
