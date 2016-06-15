from __future__ import unicode_literals
from sqlalchemy.schema import ForeignKeyConstraint, AddConstraint, DropConstraint
from dmsa.makers.generic import GenericMaker


class ForeignKeyMaker(GenericMaker):
    """A class that converts foreign key descriptions into SQLAlchemy model
    ForeignKeyConstraint classes and outputs DDL.
    """

    json = {}
    name = ''
    source_fields = []
    target_table = ''
    target_fields = []

    def __init__(self, json):
        self.json = json
        self.name = json.get('name', '')

        # chop-dbhi/data-models format.
        if 'source_field' in json:
            self.source_fields = [json['source_field']]
        if 'target_field' in json:
            self.target_fields = [json['target_field']]
        self.target_table = json.get('target_table', '')

        # JSON Table Schema format.
        if isinstance(json.get('fields'), (list, tuple)):
            self.source_fields = json['fields']
        elif isinstance(json.get('fields'), str):
            self.source_fields = [json['fields']]
        if 'reference' in json:
            if isinstance(json['reference'].get('fields'), (list, tuple)):
                self.source_fields = json['reference']['fields']
            elif isinstance(json['reference'].get('fields'), str):
                self.source_fields = [json['reference']['fields']]
            self.target_table = json['reference'].get('resource', '')

    def verify(self):
        if not self.name:
            raise RuntimeError('will not create a foreign key without an '
                               'explicit name')
        if not self.source_fields:
            raise RuntimeError('cannot create a foreign key without source '
                               'field references')
        if not self.target_fields:
            raise RuntimeError('cannot create a foreign key without target '
                               'field references')
        if not self.target_table:
            raise RuntimeError('cannot create a foreign key without a target '
                               'table reference')

    def model(self):
        self.verify()
        target_references = ['%s.%s'.format(self.target_table, f) for f in
                             self.target_fields]
        return ForeignKeyConstraint(self.source_fields, target_references,
                                    self.name, use_alter=True)

    def create_ddl(self, engine):
        self.verify()
        return str(AddConstraint(self.model()).compile(
            dialect=engine.dialect)).strip()

    def drop_ddl(self, engine):
        self.verify()
        return str(DropConstraint(self.model()).compile(
            dialect=engine.dialect)).strip()
