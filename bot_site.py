import os

from flask import render_template, request
from data.users import User
from flask import Flask
from data import db_session
from waitress import serve

db_session.global_init("db/blogs.sqlite")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

list_ = []


@app.route('/', methods=['GET'])
def index():
    try:
        global list_
        session = db_session.create_session()
        users = session.query(User).all()

        for u in users:
            list_.append([u.name, u.lvl, u.xp])

        list_.sort(key=lambda a: a[1])
        list_.reverse()
        for i in range(len(list_)):
            list_[i].append(str(i + 1))

        return render_template('index.html', title='leader board', listt=list_)
    except Exception:
        return "Временно не работает"


@app.route('/', methods=['POST'])
def search():
    try:
        new_list = []
        text = request.form.get('q')
        for u in list_:
            if text in u[0] or u[0] in text:
                new_list.append(u)
        new_list.sort(key=lambda a: a[3])
        new_list.reverse()
        if new_list == []:
            return render_template('if_empty.html')
        return render_template('index.html', title='leader board', listt=new_list)

    except Exception:
        return "Временно не работает"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    serve(app, host='localhost', port=port)
