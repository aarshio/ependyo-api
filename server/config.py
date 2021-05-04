import os

class Config:
    SECRET_KEY = '74d05d9f7bbd23126bf5968baaa1eeb3'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'ependyo.help'
    MAIL_PASSWORD = 'Ependyo@171'