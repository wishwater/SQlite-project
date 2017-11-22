# -*- coding:utf-8 -*-
from schematics.models import Model

from models.base_manager import SNBaseManager
from models.models import UserModel, UserAddModel, UserType
from models.executeSqlite3 import executeSelectOne, executeSelectAll, executeSQL
from models.user_friend_manager import UserRelationManager


class UserManager(SNBaseManager):
    user_type = UserType()
    user_type.id = 1
    user_type.type_name = 'test'
    load_models = {}

    def __init__(self):
        self.object = UserModel()

    def getModelFromForm(self,form):
        self.object.first_name = form.get('first_name', '')
        self.object.last_name = form.get('last_name', '')
        self.object.type = self.user_type
        self.object.email = form.get('email', '')
        self.object.nickname = form.get('nickname', '')
        self.object.descr = form.get('descr', '')
        if form.get('passw1', '') == form.get('passw2', ''):
            self.object.password = form.get('passw1', '')
        return self

    def add_friend(self, id=None, nickname=None):
        if not (id or nickname):
            return
        relationManager = UserRelationManager()
        relationManager.addFriend(self.object.id, id)


    def get_friends(self):
        relationManager = UserRelationManager()
        return relationManager.getFriends(self.object.id)


    def check_user(self):
        self.select().And([('nickname','=',self.object.nickname),('email','=',self.object.email)]).run()
        print(self.object.id)
        if self.object.id:
            return True
        return False

    def loginUser(self,lofin_form):
        email = lofin_form.get('email', '')
        password = lofin_form.get('passw', '')
        self.select().And([('email','=',email),('password','=',password)]).run()
        if self.object.id:
            self.load_models[self.object.nickname] = self
            return True
        return False



if __name__ == '__main__':
    manager = UserManager()
    manager.object.id = 1


