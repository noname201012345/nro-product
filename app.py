import os
from flask import Flask
from flask_login import LoginManager
from threading import Thread
import threading
from dotenv import load_dotenv

from models import db, User

# db = SQLAlchemy("sqlite:///db.sqlite")
# db = SQLAlchemy(os.getenv("DATABASE_URL", "sqlite:///db.sqlite"))  # this connects to a database either on Heroku or on localhost
load_dotenv()

def create_app():
    app = Flask(__name__)

    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SECRET_KEY'] = os.getenv("secret")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("link")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)


    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # blueprint for auth routes in our app
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from auth import getter
    t = threading.Thread(target=getter)
    t.start()
    # blueprint for non-auth parts of app 
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app

 
if __name__ == '__main__':
    app = create_app()
    app.run(host="0.0.0.0",port=8080,debug=True)