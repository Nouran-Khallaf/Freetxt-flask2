from flask import Blueprint
from flask import render_template
from flask import request
from models import *

posts = Blueprint('posts',__name__, template_folder = ('templates'))

@posts.route('/')
def posts_list():
    word = request.args.get('word')
    posts = Post.query.all()
    return render_template('posts/posts.html', posts =posts)

@posts.route('/<slug>')
def posts_detail(slug):
    posts = Post.query.all()
    post = Post.query.filter(Post.slug==slug).first()