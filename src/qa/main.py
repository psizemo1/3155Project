from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user

from . import db
from .models import Post, Group

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


"""
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(1000))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(10))
    password = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.now())


class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    description = db.Column(db.String(1000))
    users = db.relationship('User', secondary='group_user', backref='groups')


class GroupUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
"""


@main.route('/posts', methods=['GET', 'POST'])
def posts():
    user_groups = Group.query.filter(Group.users.any(id=current_user.id)).all()
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        group_id = request.form['group_id']
        # Verify that the user is in the group
        group = None
        for g in user_groups:
            if str(g.id) == str(group_id):
                group = g
                break
        if group is None:
            return render_template('403.html'), 403
        post = Post(title=title, content=content, user=current_user, group=group)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.post', post_id=post.id))
    # Get posts in descending order
    posts = sorted(Post.query.all(), key=lambda p: p.created_at, reverse=True)
    return render_template('posts.html', posts=posts, user_groups=user_groups)


@main.route('/post_edit/<post_id>', methods=['GET', 'POST'])
def post_edit(post_id):
    post = Post.query.get(post_id)
    if post is None:
        return render_template('404.html'), 404
    if post.user != current_user:
        return render_template('403.html'), 403
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        post.title = title
        post.content = content
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.post', post_id=post.id))
    return render_template('post_edit.html', post=post)


@main.route('/post_delete/<post_id>', methods=['GET', 'POST'])
def post_delete(post_id):
    post = Post.query.get(post_id)
    if post is None:
        return render_template('404.html'), 404
    if post.user != current_user:
        return render_template('403.html'), 403
    if request.method == 'POST':
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('main.posts'))
    return render_template('post_delete.html', post=post)


@main.route('/posts/<post_id>')
def post(post_id):
    post = Post.query.get(post_id)
    if post is None:
        return render_template('404.html'), 404
    return render_template('post.html', post=post)
