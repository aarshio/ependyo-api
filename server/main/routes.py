from flask import request, jsonify, Blueprint
from server import current_app, cors, db, bcrypt
from server.models import User, Post, Item, Comment, PostLike, PostDislike, CommentLike, CommentDislike
# from flask_login import login_user,current_user, logout_user, login_required
import jwt
import datetime
from functools import wraps
import uuid
import json

main = Blueprint('main', __name__)

@main.route('/api/')
def landing():
    return 'FLASK'
