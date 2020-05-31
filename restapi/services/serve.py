from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from services.config import Development

app = Flask(__name__)
app.config.from_object(Development)

CORS(app)
db = SQLAlchemy(app)
Migrate(app,db)
api = Api(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
