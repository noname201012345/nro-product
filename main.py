# flask for build webpage with index.html in templates folder
from flask import Flask, render_template, url_for, request, redirect, session, g, Blueprint
# from flask_bootstrap import Bootstrap
import sqlite3

main = Blueprint('main', __name__)
# app = Flask(__name__, static_folder='static')
# bootstrap = Bootstrap(app)
@main.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')

@main.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        print(request.form.__dict__, flush=True)
        print('!', flush=True)
        # username = request.form['username']
        # password = request.form['password']
        # print(username, password)
        # conn = get_db_connection()
        # cursor = conn.cursor()
        # cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        # user = cursor.fetchone()
        # if user:
        #     session['user_id'] = user['id']
        #     return redirect(url_for('index'))
        # else:
        #     return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == '__main__':
    main.run(debug=True)