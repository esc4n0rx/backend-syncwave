import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'sua_chave_secreta_aqui'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'sua_jwt_secret_key_aqui'
