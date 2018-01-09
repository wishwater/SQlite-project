# -*- coding:utf-8 -*-


from models.models import UserRelation

from models.base_manager import SNBaseManager

class UserRelationManager(SNBaseManager):


    def __init__(self):
        self.object = UserRelation()

    def addFriend(self,user,friend):
        if not (isinstance(user, int) and isinstance(friend, int)):
            return
        if self.getFriend(user, friend):
            return
        self.object.user = user
        self.object.friend = friend

        return self.saveFriends(user,friend)

    def saveFriends(self, user, friend):
        sql = self.insert_sql.format(self.object._name, self._sqlValues(self.insert_sql_values))
        return "ok"

    def delFriend(self, user, friend):
        if not (isinstance(user, int) and isinstance(friend, int)):
            return

        return self.delete().And([('user','=',user),('friend','=',friend)])\
            .Or([('user','=',friend),('friend','=',user)]).run()

    def getFriends(self, user):
        if not isinstance(user, int):
            return

        return self.select().And([('user','=',user)]).Or([('friend','=',user)]).run()

    def getFriend(self, user, friend):
        if not (isinstance(user, int) and isinstance(friend, int)):
            return

        return self.select().And([('user', '=', user), ('friend', '=', friend)]) \
            .Or([('user', '=', friend), ('friend', '=', user)]).run()


    def isFriend(self, user, friend):
        if not (isinstance(user, int) and isinstance(friend, int)):
            return

        data = self.select().And([('user', '=', user), ('friend', '=', friend)]) \
            .Or([('user', '=', friend), ('friend', '=', user)]).run()

        if data:
            return True
        return False

    def blockFriend(self,user, friend):
        if not (isinstance(user, int) and isinstance(friend, int)):
            return

        relation = self.getFriend(user,friend)
        relation.object.block = 1
        relation.save()
