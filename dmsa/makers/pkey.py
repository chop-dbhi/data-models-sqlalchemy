from __future__ import unicode_literals
from sqlalchemy.schema import PrimaryKeyConstraint, AddConstraint, DropConstraint
from dmsa.makers.generic import GenericMaker


class PrimaryKeyMaker(GenericMaker):
    """A class that converts primary key descriptions into SQLAlchemy model
    PrimaryKeyConstraint classes and outputs DDL.
    """

    model_func = PrimaryKeyConstraint
    model_readable = 'primary key'
    create_ddl_func = AddConstraint
    drop_ddl_func = DropConstraint
