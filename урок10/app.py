# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect, url_for, session
from models.executeSqlite3 import executeSelectOne, executeSelectAll, executeSQL
from functools import wraps
from models.user_manager import UserManager
from models.user_friend_manager import UserRelationManager
import os

# створюємо головний об'єкт сайту класу Flask
app = Flask(__name__)
# добавляємо секретний ключ для сайту щоб шифрувати дані сессії
# при кожнаму сапуску фласку буде генечитись новий рандомний ключ з 24 символів
# app.secret_key = os.urandom(24)
app.secret_key = '125'


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'username' in session:
            if UserManager.load_models.get(session['username'], None):
                return f(*args, **kwargs)
        return redirect(url_for('login'))
    return wrap


# описуємо логін роут
# вказуємо що доступні методи "GET" і "POST"
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        # якщо метод пост дістаємо дані з форми і звіряємо чи є такий користвач в базі данних
        # якшо є то в дану сесію добавляєм ключ username
        # і перекидаємо користувача на домашню сторінку
        user = UserManager()
        if user.loginUser(request.form):
            addToSession(user)
            return redirect(url_for('home'))

    return render_template('login.html')

# описуємо роут для вилогінення
# сіда зможуть попадати тільки GET запроси
@app.route('/logout')
@login_required
def logout():
    user = session.get('username', None)
    if user:
        # якщо в сесії є username тоді видаляємо його
        del session['username']
    return redirect(url_for('login'))

@app.route('/add_friend', methods=["GET","POST"])
@login_required
def add_friend():
    if request.method == 'POST':
        user_nickname = session['username']
        user = UserManager()
        if user.SelectUser(user_nickname):
            user_id = user.object.id
        friend_nickname = request.form['friend_nickname']
        friend = UserManager()
        if friend.SelectUser(friend_nickname):
            friend_id = friend.object.id
        friend = UserRelationManager()
        if user_id and friend_id:
            friend.addFriend(user_id , friend_id)
            return('ok')
        return('!ok')
    else:
        render_template('home.html')

@app.route('/find_friend', methods = ["GET","POST"])
@login_required
def find_friend():
    if request.method == 'GET':
        user_nickname = session['username']
        user = UserManager()
        if user.SelectUser(user_nickname):
            user_id = user.object.id
        friend_nickname = request.args['friend_nickname']
        friend = UserManager()
        if friend.SelectUser(friend_nickname):
            friend_id = friend.object.id
        friend = UserRelationManager()
        if user_id and friend_id:
            IsItYourFriend = friend.isFriend(user_id , friend_id)
            print(IsItYourFriend)
            if IsItYourFriend == True:
                return redirect(url_for('nickname', nickname = friend_nickname))
            else:
                #context = {'Error': []}
               # context['Error:'].append("you don't have friend with that nickname")
                render_template('find_friend error.html')
                return("you do not have friends with this nickname")

@app.route('/delete_friend', methods=["GET","POST"])
@login_required
def delete_friend():
    if request.method == 'POST':
        user_nickname = session['username']
        user = UserManager()
        if user.SelectUser(user_nickname):
            user_id = user.object.id
        friend_id = request.form['friend_id']
        friend = UserRelationManager()
        if user_id and friend_id:
            friend.delFriend(user_id , friend_id)
            return('ok')
        return('!ok')
    else:
        render_template('home.html')

@app.route('/block_friend', methods=["GET","POST"])
@login_required
def block_friend():
    if request.method == 'POST':
        user_nickname = session['username']
        user = UserManager()
        if user.SelectUser(user_nickname):
            user_id = user.object.id
        friend_id = request.form['friend_id']
        friend = UserRelationManager()
        if user_id and friend_id:
            friend.blockFriend(user_id , friend_id)
            return('ok')
        return('!ok')
    else:
        render_template('home.html')

@app.route('/friends_view',methods = ["GET","POST"])
@login_required
def friends_view():
    user_nickname = session['username']
    print(user_nickname)
    user = UserManager()
    if user.SelectUser(user_nickname):
        user_id = user.object.id
    user = UserRelationManager()
    friends = user.getFriends(user_id)
    print(friends.object)
    print(friends)

@app.route('/<nickname>',methods=["GET","POST"])
@login_required
def nickname(nickname):
    context = {}
    if session.get('username', None):
        user = UserManager.load_models[session['username']]
        context['loginUser'] = user

    if request.method == "POST":
        nickname = request.form.get('nickname')

    selectUser = UserManager()
    selectUser.select().And([('nickname','=',nickname)]).run()
    context['user'] = selectUser

    return render_template('home.html', context=context)

# описуємо домашній роут
# сіда зможуть попадати тільки GET запроси
@app.route('/')
@login_required
def home():
    context = {}
    if session.get('username', None):
        user = UserManager.load_models[session['username']]
        # якщо в сесії є username тоді дістаємо його дані
        # добавляємо їх в словник для передачі в html форму
        context['user'] = user
        context['loginUser'] = user
    return render_template('home.html', context=context)

def addToSession(user):
    session['username'] = user.object.nickname

@app.route('/edit', methods=["GET", "POST"])
@login_required
def edit():
    nickname = session['username']
    context = {}
    user = UserManager()
    if user.SelectUser(nickname):
            context['user'] = user
    if request.method == 'POST':
        user = user.getModelFromForm(request.form)
        if user.save():
            context['user'] = user
            return redirect(url_for('home'))
    return render_template('edit.html', context=context)

@app.route('/registration', methods=["GET", "POST"])
def registr():
    context = {'Error': []}
    if request.method == 'POST':
        user = UserManager().getModelFromForm(request.form)
        if user.check_user():
            context['Error'].append('wrong nickname or email')
        if not user.object.password:
            context['Error'].append('incorrect password')
        if context['Error']:
            return render_template('registration.html', context=context)
        if user.save():
            UserManager.load_models[user.object.nickname] = user
            addToSession(user)
            return redirect(url_for('home'))

        context['Error'].append('incorrect data')
    return render_template('registration.html', context=context)


if __name__ == '__main__':
    app.run(debug=True, port=5034)
