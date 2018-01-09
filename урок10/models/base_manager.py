# -*- coding:utf-8 -*-
from schematics.models import Model
from schematics.types import ModelType

from models.bool_where import BoolWhereDelete , BoolWhereSelect
from .models import UserModel, UserAddModel, UserType
from .executeSqlite3 import executeSelectOne, executeSelectAll, executeSQL
from .my_types import One2One




class SNBaseManager():
    update_sql = 'UPDATE {} SET {} WHERE id = {}'
    update_sql_set = ' {0} = {1} '
    insert_sql = 'INSERT INTO {} VALUES ({})'
    insert_sql_values = '{1}'

    def __init__(self, class_model=None):
        self.object = class_model()

    def itemToUpdate(self):
        atoms = self.object.atoms()
        result = []
        for item in atoms:
            if item.field.typeclass != One2One:
                result.append(item.name)
        return result

    def _chooseTemp(self, item):
        if isinstance(item, type(None)):
            return 'NULL'
        elif isinstance(item, dict):
            return item['id']
        elif isinstance(item, int):
            return item
        return repr(str(item))

    def _sqlValues(self, template):
        keys = self.itemToUpdate()
        primitive = self.object.to_primitive()
        result = '{},' * len(keys)
        result = result.rstrip(',')
        return result.format(*[template.format(key, self._chooseTemp(primitive[key])) for key in keys])

    def save(self):
        if self.object.id:
            sql = self.update_sql.format(self.object._name, self._sqlValues(self.update_sql_set), self.object.id)
        else:
            sql = self.insert_sql.format(self.object._name, self._sqlValues(self.insert_sql_values))
        print(sql)
        return executeSQL(sql)

    def update(self):
        sql = self.update_sql.format(self.object._name, self._sqlValues(self.update_sql_set), self.object.id)

    def delete(self):
        return BoolWhereDelete(self)

    def _delete(self,sql):
        return executeSQL(sql)

    def fillModel(self, sql):
        resultd = {}
        resultl = []
        atoms = self.object.atoms()
        datal = executeSelectAll(sql)
        for data in datal:
            for atom in atoms:
                if atom.field.typeclass == ModelType:
                    man = SNBaseManager(atom.field.model_class)
                    sql = man.select().And([('id', '=', data[atom.name])]).sql
                    raw_data = executeSelectAll(sql)
                    if raw_data:
                        raw_data = raw_data[0]
                    resultd[atom.name] = atom.field.model_class().import_data(raw_data=raw_data)
                elif atom.field.typeclass == One2One:
                    man = SNBaseManager(atom.field.model_class)
                    sql = man.select().And([('id', '=', data['id'])]).sql
                    raw_data = executeSelectAll(sql)
                    if not raw_data:
                        raw_data = {}
                    resultd[atom.name] = atom.field.model_class().import_data(raw_data)
                else:
                    resultd[atom.name] = data[atom.name]
            resultl.append(resultd)

        if resultd:
            self.object.import_data(resultd)

    def select(self):
        return BoolWhereSelect(self)


if __name__ == '__main__':
    man = SNBaseManager(UserModel)
    typep = UserType()
    typep.id = 1
    typep.name = 'test'

    # man.object.id = 1
    man.object.first_name = 'test'
    man.object.last_name = 'test'
    man.object.type = typep
    man.object.descr = 'test'
    man.object.user_photo = 'test'
    man.object.user_photos = ['test']
    man.object.email = 'testtest.test'
    man.object.nickname = 'test'
    man.object.password = 'test'
    man.object.user_add = UserAddModel()
    atoms = man.object.atoms()
    for i in atoms:
        if i.field.typeclass == One2One:
            print(i.field.__dict__)
            print(i.field.typeclass)
            print(i.field.model_class._name)
