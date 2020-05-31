class Config:
    DEBUG = False
    JWT_SECRET_KEY = 'mysecretkey'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
    SQLACHEMY_TRACK_MODIFICATIONS = False

class Development(Config):
    DEBUG = True

class Production(Config):
    DEBUG = False
