from __future__ import unicode_literals
from sqlalchemy.schema import UniqueConstraint, AddConstraint, DropConstraint
from dmsa.makers.generic import GenericMaker


class UniqueMaker(GenericMaker):
    """A class that converts constraint descriptions into SQLAlchemy model
    UniqueConstraint classes and outputs DDL.
    """

    model_func = UniqueConstraint
    model_readable = 'unique constraint'
    create_ddl_func = AddConstraint
    drop_ddl_func = DropConstraint
