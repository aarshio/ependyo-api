from flask import request, jsonify, Blueprint, session
from server import db
from server.models import User, Post, Item, Comment, PostLike, PostDislike, CommentLike, CommentDislike
import uuid

posts = Blueprint('posts', __name__)

@posts.route('/api/home', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        res = [z.to_json() for z in User.query]
        return jsonify({'posts': res})

    return jsonify({'error': "invalid"})

@posts.route('/api/post_item', methods=['GET', 'POST'])
def post_item():
    if request.method == 'POST':
         init_data = request.get_json(silent=True)
         data = {'item': init_data.get('item'), 'rating': init_data.get(
            'rating'),'headline': init_data.get('headline'), 'content': init_data.get('content'), 'username': init_data.get('username')}
         user = User.query.filter_by(username=data['username']).first()
         item = Item.query.filter_by(name=data['item']).first()
         post = Post(id=uuid.uuid4().hex, name=data['headline'], content=data['content'], rating=data['rating'], post_file={"urls":[1,2,3]}, post_user=data['username'], post_item=item.id)
         
         if item.rating['overall']<0:
             item.num_posts = 1
             new_rating = {}
             for feature in item.rating:
                if feature in data['rating']:
                    new_rating[feature] = data['rating'][feature]
             item.rating = new_rating
         else:
            item.num_posts += 1
            new_rating = {}
            for feature in item.rating:
                if feature in data['rating']:
                    new_rating[feature] = round((((item.rating[feature] * (item.num_posts -1)) + data['rating'][feature])/item.num_posts),2)
            item.rating = new_rating


         db.session.add(post)
         db.session.commit()

         return jsonify({'status':'200'})

@posts.route('/api/all_posts', methods=['GET', 'POST'])
def all_posts():
    if request.method == 'GET':
        posts = [z.to_json() for z in Post.query]
        return jsonify({'posts':list(posts)})
    return jsonify({'posts':'invalid'})


@posts.route('/api/get_post', methods=['GET', 'POST'])
def get_post():
    if request.method == 'GET':
         post_id = request.args.get('id')
         post = Post.query.get(post_id)
         item = Item.query.get(post.post_item)
         return jsonify({'post':post.to_json(), 'item':item.to_json()})


@posts.route('/api/post_comment', methods=['GET', 'POST'])
def post_comment():
    if request.method == 'POST':
         init_data = request.get_json(silent=True)
         data = {'username': init_data.get('username'),'post_id': init_data.get('post_id')[4:], 'comment': init_data.get(
            'comment')}
         comment = Comment(id=uuid.uuid4().hex, content=data['comment'], comment_post=data['post_id'], comment_user=data['username'] )
         db.session.add(comment)
         db.session.commit()
         post = Post.query.get(data['post_id'])
         return jsonify({'post':post.to_json()})


@posts.route('/api/post_like', methods=['GET', 'POST'])
def post_like():
    if request.method == 'POST':
         init_data = request.get_json(silent=True)
         data = {'username': init_data.get('username'),'post_id': init_data.get('post_id')[4:]}
         user = User.query.filter_by(username=data['username']).first()
         post = Post.query.get(data['post_id'])
         if user.has_liked_post(PostLike, post) == False:
             if user.has_liked_post(PostDislike, post) == False:
                like = PostLike(username=data['username'], post_id=data['post_id'])
                db.session.add(like)
                db.session.commit()
             else:
                 user.unlike_post(PostDislike,post)
                 like = PostLike(username=data['username'], post_id=data['post_id'])
                 db.session.add(like)
                 db.session.commit()

         return jsonify({'post':post.to_json()})              

@posts.route('/api/post_dislike', methods=['GET', 'POST'])
def post_dislike():
    if request.method == 'POST':
         init_data = request.get_json(silent=True)
         data = {'username': init_data.get('username'),'post_id': init_data.get('post_id')[4:]}
         user = User.query.filter_by(username=data['username']).first()
         post = Post.query.get(data['post_id'])
         if user.has_liked_post(PostDislike, post) == False:
             if user.has_liked_post(PostLike, post) == False:
                dislike = PostDislike(username=data['username'], post_id=data['post_id'])
                db.session.add(dislike)
                db.session.commit()
             else:
                 user.unlike_post(PostLike, post)
                 dislike = PostDislike(username=data['username'], post_id=data['post_id'])
                 db.session.add(dislike)
                 db.session.commit()

         return jsonify({'post':post.to_json()})      

@posts.route('/api/comment_like', methods=['GET', 'POST'])
def comment_like():
    if request.method == 'POST':
         init_data = request.get_json(silent=True)
         data = {'username': init_data.get('username'),'comment_id': init_data.get('comment_id')}
         user = User.query.filter_by(username=data['username']).first()
         comment = Comment.query.get(data['comment_id'])
         if user.has_liked_comment(CommentLike, comment) == False:
             if user.has_liked_comment(CommentDislike, comment) == False:
                like = CommentLike(username=data['username'], comment_id=data['comment_id'])
                db.session.add(like)
                db.session.commit()
             else:
                 user.unlike_comment(CommentDislike,comment)
                 like = CommentLike(username=data['username'], comment_id=data['comment_id'])
                 db.session.add(like)
                 db.session.commit()

         return jsonify({'comment':comment.to_json()})

@posts.route('/api/comment_dislike', methods=['GET', 'POST'])
def comment_dislike():
    if request.method == 'POST':
         init_data = request.get_json(silent=True)
         data = {'username': init_data.get('username'),'comment_id': init_data.get('comment_id')}
         user = User.query.filter_by(username=data['username']).first()
         comment = Comment.query.get(data['comment_id'])
         if user.has_liked_comment(CommentDislike, comment) == False:
             if user.has_liked_comment(CommentLike, comment) == False:
                dislike = CommentDislike(username=data['username'], comment_id=data['comment_id'])
                db.session.add(dislike)
                db.session.commit()
             else:
                 user.unlike_comment(CommentLike, comment)
                 dislike = CommentDislike(username=data['username'], comment_id=data['comment_id'])
                 db.session.add(dislike)
                 db.session.commit()

         return jsonify({'comment':comment.to_json()})


@posts.route('/api/delete_post', methods=['GET', 'POST'])
def delete_post():
    if request.method == 'POST':
         init_data = request.get_json(silent=True)
         data = { 'post_id' : init_data.get('post_id')[4:]}
         post = Post.query.get(data['post_id'])
         item = Item.query.get(post.post_item)
         new_rating = {}
         if(item.num_posts > 1):
            for feature in ['design', 'durability', 'camera', 'features', 'battery', 'performance', 'overall']:
                    new_rating[feature] = round(((item.rating[feature] * item.num_posts) - post.rating[feature])/(item.num_posts-1), 2)
        
         if(item.num_posts == 1):
            for feature in ['design', 'durability', 'camera', 'features', 'battery', 'performance', 'overall']:
                    new_rating[feature] = -1
         item.num_posts -= 1
         item.rating = new_rating    

         Post.query.filter_by(id=data['post_id']).delete()

         db.session.commit()
         return jsonify({'status':"deleted"})



@posts.route('/api/delete_comment', methods=['GET', 'POST'])
def delete_comment():
    if request.method == 'POST':
         init_data = request.get_json(silent=True)
         data = { 'comment_id' : init_data.get('id')}
         comment =  Comment.query.filter_by(id=data['comment_id']).first()
         post = Post.query.get(comment.comment_post)  
         Comment.query.filter_by(id=data['comment_id']).delete()
         db.session.commit()
         return jsonify({'post': post.to_json()})