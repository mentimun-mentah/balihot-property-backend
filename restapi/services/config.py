from os import getenv

class Config:
    DEBUG = False
    SECRET_KEY = getenv('SECRET_KEY')
    JWT_SECRET_KEY = getenv('JWT_SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = 1 * 86400  # 1 days
    JWT_REFRESH_TOKEN_EXPIRES = 30 * 86400  # 30 days
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

class Development(Config):
    DEBUG = True

class Production(Config):
    PROPAGATE_EXCEPTIONS = True
