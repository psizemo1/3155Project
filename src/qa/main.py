from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user

from . import db
from .models import Post, Group

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/posts', methods=['GET', 'POST'])
def posts():
    if current_user.is_anonymous:
        user_groups = []
    else:
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
    search_query = request.args.get('q')
    if search_query:
        posts = Post.search(search_query)
    else:
        posts = sorted(Post.query.filter(Post.parent == None).all(), key=lambda p: p.created_at, reverse=True)
    return render_template('posts.html', posts=posts, user_groups=user_groups)


@main.route('/posts/<post_id>/edit', methods=['GET', 'POST'])
def post_edit(post_id):
    post = Post.query.get(post_id)
    if post is None:
        return render_template('404.html'), 404
    if post.user != current_user:
        return render_template('403.html'), 403
    if request.method == 'POST':
        title = '' if post.parent else request.form['title']
        content = request.form['content']
        post.title = title
        post.content = content
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.post', post_id=post.id))
    return render_template('post_edit.html', post=post)


@main.route('/posts/<post_id>/delete', methods=['GET', 'POST'])
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


@main.route('/posts/<post_id>/reply', methods=['GET', 'POST'])
def reply(post_id):
    if current_user.is_anonymous:
        return render_template('403.html'), 403
    post = Post.query.get(post_id)
    if post is None:
        return render_template('404.html'), 404
    if request.method == 'POST':
        content = request.form['content']
        child = Post(title="", content=content, group=post.group, user=current_user, parent=post)
        db.session.add(child)
        db.session.commit()
        return redirect(url_for('main.post', post_id=post.id))
    return redirect(url_for('main.post', post_id=post.id))
