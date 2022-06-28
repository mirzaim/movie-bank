from email import message
from time import time
from pymongo import MongoClient
from os import getenv
from flask import Flask, request, abort, jsonify
from random import randrange
import sys
import hashlib
from functools import reduce

from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token


mongo_client = MongoClient('db',
                            username=getenv('MONGO_INITDB_ROOT_USERNAME'),
                            password=getenv('MONGO_INITDB_ROOT_PASSWORD'))
db = mongo_client[getenv('MONGO_INITDB_DATABSE')]

movies = db.movies
votes = db.votes
comments = db.comments
users = db.users

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super-secret'
jwt = JWTManager(app)

@app.route("/")
def index():
    # just for test
    return jsonify(message='TEST', users=list(users.find({}, {'_id': False})), 
                   movies=list(movies.find({}, {'_id': False})),
                   comments=list(comments.find({}, {'_id': False}))
    ) 
    # return jsonify(message='Wellcome')

@app.route("/login", methods=["POST"])
def login():

    json_data = request.get_json()

    try:
        username, password = json_data['username'], json_data['password']
    except:
        abort(400, description='Invalid parameters provided')
    
    user = users.find_one({'username': username})
    if not user or hashlib.sha256(password.encode('utf-8')).hexdigest() != user['password']:
        return jsonify(message='Bad username or password.')

    access_token = create_access_token(identity=user['username'])
    return jsonify(access_token=access_token)

@app.route("/protected", methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user)

@app.route("/admin/movie", methods=["POST"])
@jwt_required()
def add_new_movie():
    current_user = get_jwt_identity()

    user = users.find_one({'username': current_user})
    if not user or user['role'] != 'admin':
        abort(400, "permision needed.")
    
    json_data = request.get_json()

    try:
        name, description = json_data['name'], json_data['description']
    except:
        abort(400, description='Invalid parameters provided')
    
    
    while movies.find_one({'movie_id': (id := randrange(1000000))}):
        pass
    movies.insert_one({'movie_id': id, 'name': name, 'description': description, 'rating': 0.0})
    
    return jsonify(message=f'{name} is added to movie list with id "{id}".'), 204

@app.route('/admin/movie/<int:movie_id>', methods=['PUT'])
@jwt_required()
def update_movie(movie_id: int):
    current_user = get_jwt_identity()

    user = users.find_one({'username': current_user})
    if not user or user['role'] != 'admin':
        abort(400, "permision needed.")
    
    json_data = request.get_json()

    try:
        name, description = json_data['name'], json_data['description']
    except:
        abort(400, description='Invalid parameters provided')
    
    movie = movies.find_one({'movie_id': movie_id})

    if not movie:
        return jsonify(message=f'no movie with id "{movie_id}".')
    
    movies.find_one_and_update({'movie_id': movie_id}, {'$set': {'name': name, 'description': description}})

    return jsonify(message=f'movie with id "{movie_id}" is updated.'), 204

@app.route('/admin/movie/<int:movie_id>', methods=['DELETE'])
@jwt_required()
def delete_movie(movie_id: int):
    current_user = get_jwt_identity()

    user = users.find_one({'username': current_user})
    if not user or user['role'] != 'admin':
        abort(400, "permision needed.")

    movie = movies.find_one({'movie_id': movie_id})

    if not movie:
        return jsonify(message=f'no movie with id "{movie_id}".')
    
    movies.find_one_and_delete({'movie_id': movie_id})

    return jsonify(message=f'movie with id "{movie_id}" is deleted.'), 204

@app.route('/admin/comment/<int:comment_id>', methods=['PUT'])
@jwt_required()
def update_comment(comment_id: int):
    current_user = get_jwt_identity()

    user = users.find_one({'username': current_user})
    if not user or user['role'] != 'admin':
        abort(400, "permision needed.")

    json_data = request.get_json()

    try:
        approved = json_data['approved']
    except:
        abort(400, description='Invalid parameters provided')
    
    result = comments.find_one_and_update({'id': comment_id}, {"$set": {"approved": approved}})

    if not result:
        return jsonify(message='invalid comment id.')
    
    return jsonify('comment approved field updated.'), 204

@app.route('/admin/comment/<int:comment_id>', methods=['DELETE'])
@jwt_required()
def delete_comment(comment_id: int):
    current_user = get_jwt_identity()

    user = users.find_one({'username': current_user})
    if not user or user['role'] != 'admin':
        abort(400, "permision needed.")
    
    result = comments.find_one_and_delete({'id': comment_id})

    if not result:
        return jsonify(message='invalid comment id.')

    return jsonify(message=f'comment with id {comment_id} is removed.'), 204

@app.route('/user/vote', methods=['POST'])
@jwt_required()
def add_new_vote():
    current_user = get_jwt_identity()

    user = users.find_one({'username': current_user})
    if not user or user['role'] != 'user':
        abort(400, "permision needed.")

    json_data = request.get_json()

    try:
        movie_id, vote = json_data['movie_id'], json_data['vote']

        if not (0 <= vote <= 10):
            raise Exception()
    except:
        abort(400, description='Invalid parameters provided')
    
    while votes.find_one({'id': (id := randrange(1000000))}):
        pass
    votes.insert_one({'id': id, 'movie_id': movie_id, 'rating': vote, 'user': user['username']})

    vote_list = list(votes.find({'movie_id': movie_id}))

    movie_score = reduce(lambda x, y: x+y['rating'], vote_list, 0) / len(vote_list)
    movies.find_one_and_update({'movie_id': movie_id}, {"$set": {"rating": movie_score/10}})
    
    return jsonify(message=f'vote is added on {movie_id} movie.')

@app.route('/user/comment', methods=['POST'])
@jwt_required()
def add_new_comment():
    current_user = get_jwt_identity()

    user = users.find_one({'username': current_user})
    if not user or user['role'] != 'user':
        abort(400, "permision needed.")

    json_data = request.get_json()

    try:
        movie_id, comment_body = json_data['movie_id'], json_data['comment_body']
    except:
        abort(400, description='Invalid parameters provided')
    
    while comments.find_one({'id': (id := randrange(1000000))}):
        pass

    # in defualt all comments are approved, admin could delete or disapprove it.
    comments.insert_one({'id': id, 'user': user['username'], 'movie_id': movie_id,
                         'comment': comment_body, 'approved': True, 'created_at': int(time())})

    return jsonify(message=f'your comment is added with id "{id}".')

@app.route('/comments', methods=['GET'])
def get_comments():
    try:
        movie_id = int(request.args.get('movie'))
    except:
        abort(400, description='Invalid parameters provided')
    
    comment_list = list(comments.find({'movie_id': movie_id, 'approved': True},
                                      {'_id': False, 'id': True, 'user': True, 'comment': True}))

    return jsonify(comment_list)

@app.route('/movies', methods=['GET'])
def get_movies_list():
    movie_list = list(movies.find({}, {'_id': False}))
    return jsonify(movie_list)

@app.route('/movie/<int:movie_id>', methods=['GET'])
def get_movie(movie_id: int):
    result_movie = movies.find_one({'movie_id': movie_id}, {'_id': False})
    if not result_movie:
        abort(400, "invalid movie id.")
    return jsonify(result_movie)

if __name__ == '__main__':
    users.delete_one({'username': 'admin'})
    users.delete_one({'username': 'morteza'})
    users.delete_one({'username': 'moein'})
    if not users.find_one({'username': 'admin'}):
        users.insert_one({'id': 0, 'username': 'admin', 'password': hashlib.sha256('admin'.encode('utf-8')).hexdigest(), 'role': 'admin'})
    if not users.find_one({'username': 'morteza'}):
        users.insert_one({'id': 1, 'username': 'morteza', 'password': hashlib.sha256('morteza'.encode('utf-8')).hexdigest(), 'role': 'user'})
    if not users.find_one({'username': 'moein'}):
        users.insert_one({'id': 2, 'username': 'moein', 'password': hashlib.sha256('moein'.encode('utf-8')).hexdigest(), 'role': 'user'})
    if not movies.find_one({'movie_id': 0}):
        movies.insert_one({'movie_id': 0, 'name': 'shrek', 'description': 'animaiton', 'rating': 0.0})
    if not movies.find_one({'movie_id': 1}):
        movies.insert_one({'movie_id': 1, 'name': 'shrek 2', 'description': 'animaiton', 'rating': 0.0})
    app.run(host='0.0.0.0', port=80, debug=True, use_reloader=True)