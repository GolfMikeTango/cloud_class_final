from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
import uuid

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    #set this in AWS
    app.config['SECRET_KEY'] = uuid.uuid4().hex
    #16 MB max file length
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000 
    app.config['UPLOAD_EXTENSIONS'] = ['.txt']
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    from .db_models import User

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    # Create blueprint for flaskapp (our main file)
    from .flaskapp import flaskapp as main_blueprint
    app.register_blueprint(main_blueprint)

    # Create blueprint for authentication
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app

db.create_all(app=create_app())