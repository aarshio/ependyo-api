from sqlalchemy.dialects.postgresql import ARRAY
from server import db, login_manager
from flask import current_app
from datetime import datetime
import uuid
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
# from flask_login import UserMixin

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.filter_by(username=user_id).first()


class User(db.Model):
    id = db.Column(db.String, primary_key=True, default=uuid.uuid4().hex)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    bio = db.Column(db.String(150))
    image_file = db.Column(db.String(20),default='default.jpg')
    influence = db.Column(db.Integer, default=0)
    date = db.Column(db.String(10), nullable=False, default=datetime.utcnow)
    user_post = db.relationship("Post", backref="parent_post_user", lazy=True)
    user_comment = db.relationship("Comment", backref="parent_comment_user", lazy=True)
    user_postlike = db.relationship("PostLike", backref="parent_postlike_user", lazy=True)
    user_postdislike = db.relationship("PostDislike", backref="parent_postdislike_user", lazy=True)
    user_commentlike = db.relationship("CommentLike", backref="parent_commentlike_user", lazy=True)
    user_commentdislike = db.relationship("CommentDislike", backref="parent_commentdislike_user", lazy=True)
    
    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id':self.id}).decode('utf-8')
   
    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def like_post(self, model, post):
        if not self.has_liked_post(model, post):
            like = model(username=self.username, post_id=post.id)
            db.session.add(like)

    def unlike_post(self, model,post):
        if self.has_liked_post(model, post):
            model.query.filter_by(
                username=self.username,
                post_id=post.id).delete()

    def has_liked_post(self, model, post):
        return model.query.filter(
            model.username == self.username,
            model.post_id == post.id).count() > 0

    def like_comment(self, model, comment):
        if not self.has_liked_comment(model, comment):
            like = model(username=self.username, comment_id=comment.id)
            db.session.add(like)

    def unlike_comment(self, model,comment):
        if self.has_liked_comment(model, comment):
            model.query.filter_by(
                username=self.username,
                comment_id=comment.id).delete()

    def has_liked_comment(self, model, comment):
        return model.query.filter(
            model.username == self.username,
            model.comment_id == comment.id).count() > 0

    def likes_recieved(self):
        posts = [z.to_json() for z in self.user_post]
        counter = 0
        for post in posts:
            counter +=  post['likes']
        return counter
    def to_json(self):
        return {
            "username": self.username,
            "email": self.email,
            "influence": self.influence,
            "date": self.date,
            "user_post": [z.to_json() for z in self.user_post],
            "user_comment": [z.to_json() for z in self.user_comment],
            "likes_recieved": self.likes_recieved(),
            "bio": self.bio
        }
    def user_post_to_json(self):
        return {"user_post" : [z.to_json() for z in self.user_post]}

    def __repr__(self):
        return f"User('{self.username}','{self.email}','{self.image_file}','{self.influence}', '{self.user_post}')"


class Item(db.Model):
    id = db.Column(db.String, primary_key=True, default=uuid.uuid4().hex)
    name = db.Column(db.String(20), unique=True, nullable=False)
    category = db.Column(db.String(20), nullable=False)
    details = db.Column(db.PickleType())
    rating = db.Column(db.PickleType())
    num_posts = db.Column(db.Integer, default=0)
    item_file = db.Column(db.PickleType())
    item_post = db.relationship("Post", backref="parent_post_item", lazy=True)

    def to_json(self):
        return {
            "id":self.id,
            "name": self.name,
            "num": self.num_posts,
            "category": self.category,
            "details": self.details,
            "rating": self.rating,
            "item_file" : self.item_file,
        }
    def item_post_to_json(self):
        return{"item_post" : [z.to_json() for z in self.item_post]}

    
    def __repr__(self):
        return f"Item('{self.name}', '{self.category}', '{self.details}', '{self.rating}', '{self.item_file}', '{self.item_post}')"


class Post(db.Model):
    id = db.Column(db.String, primary_key=True, default=uuid.uuid4().hex)
    name = db.Column(db.String(20), nullable=False)
    content = db.Column(db.String(100000000), nullable=False)
    date = db.Column(db.String(10), nullable=False, default=datetime.utcnow)
    # reaction = db.Column(db.PickleType())
    rating = db.Column(db.PickleType())
    likes = db.relationship('PostLike', backref='post', lazy='dynamic')
    dislikes = db.relationship('PostDislike', backref='post', lazy='dynamic')
    post_file = db.Column(db.PickleType())
    post_user = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    post_item = db.Column(db.String, db.ForeignKey('item.id'), nullable=False)
    post_comment = db.relationship("Comment", backref="parent_comment_post", lazy=True)

    def to_json(self):
        return {
            'id': self.id,
            "name": self.name,
            "content": self.content,
            "date": self.date,
            # "reaction": self.reaction,
            'likes' : self.likes.count(),
            'dislikes' : self.dislikes.count(),
            'rating' : self.rating,
            "post_file" : self.post_file,
            "post_user" : self.post_user,
            "post_item" : self.post_item,
            "post_comment" : [z.to_json() for z in self.post_comment]
        }
    def post_comment_to_json(self):
        return {"post_comment" : [z.to_json() for z in self.post_comment]}    
    def __repr__(self):
        return f"Post('{self.id}','{self.name}', '{self.content}', '{self.date}', '{self.post_file}', '{self.post_user}', '{self.post_item}', '{self.post_comment}')"    
        
class Comment(db.Model):
    id = db.Column(db.String, primary_key=True, default=uuid.uuid4().hex)
    content = db.Column(db.String(100000000), nullable=False)
    date = db.Column(db.String(10), nullable=False, default=datetime.utcnow)
    impression = db.Column(db.Integer, default=0)
    likes = db.relationship('CommentLike', backref='comment', lazy='dynamic')
    dislikes = db.relationship('CommentDislike', backref='comment', lazy='dynamic')
    comment_post = db.Column(db.String, db.ForeignKey('post.id'), nullable=False)
    comment_user = db.Column(db.String, db.ForeignKey('user.username'), nullable=False)
    def to_json(self):
        return {
            'id': self.id,
            "content": self.content,
            "date": self.date,
            'likes' : self.likes.count(),
            'dislikes' : self.dislikes.count(),
            "impression": self.impression,
            "comment_post" : self.comment_post,
            "comment_user" : self.comment_user
        } 
    def __repr__(self):
        return f"Comment('{self.id}', '{self.content}', '{self.date}', '{self.impression}', '{self.comment_post}', '{self.comment_user}')"

class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Integer, db.ForeignKey('user.username'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

class PostDislike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Integer, db.ForeignKey('user.username'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

class CommentLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Integer, db.ForeignKey('user.username'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))

class CommentDislike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Integer, db.ForeignKey('user.username'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'))