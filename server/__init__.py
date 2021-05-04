from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from server.config import Config
from flask_mail import Mail

cors = CORS()
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    cors.init_app(app, resources={r"/./*": {"origins": "*"}})
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    
    from server.users.routes import users
    from server.post.routes import posts
    from server.item.routes import items

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(items)

    return app
