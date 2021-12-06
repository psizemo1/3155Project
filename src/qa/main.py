from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import current_user

from . import db
from .models import Post, Group, Image, Vote

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
        image = request.files['image']
        # Verify that the user is in the group
        group = None
        for g in user_groups:
            if str(g.id) == str(group_id):
                group = g
                break
        if group is None:
            return render_template('403.html'), 403
        post = Post(title=title, content=content, user=current_user, group=group)
        if image:
            image_file = Image(image=image.read(), post=post)
            db.session.add(image_file)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.post', post_id=post.id))
    # Get posts in descending order
    search_query = request.args.get('q')
    if search_query:
        posts = Post.search(search_query)
    else:
        posts = sorted(Post.query.filter(Post.parent == None).all(), key=lambda p: p.created_at, reverse=True)
    sort = request.args.get('sort')
    if sort == 'votes':
        posts = sorted(posts, key=lambda p: p.score(), reverse=True)
    elif sort == 'newest':
        posts = sorted(posts, key=lambda p: p.created_at, reverse=True)
    elif sort == 'oldest':
        posts = sorted(posts, key=lambda p: p.created_at, reverse=False)
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
        image = request.files.get('image')
        if image:
            for old_image in post.images:
                db.session.delete(old_image)
            image_file = Image(image=image.read(), post=post)
            db.session.add(image_file)
        db.session.add(post)
        db.session.commit()
        if post.parent:
            return redirect(url_for('main.post', post_id=post.parent.id))
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
        if post.parent:
            return redirect(url_for('main.post', post_id=post.parent.id))
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


@main.route('/images/<image_id>.jpg')
def image(image_id):
    image = Image.query.get(image_id)
    if image is None:
        return render_template('404.html'), 404
    # Set content type to image/jpeg
    return image.image, 200, {'Content-Type': 'image/jpeg'}


@main.route('/posts/<post_id>/vote', methods=['POST'])
def vote(post_id):
    post = Post.query.get(post_id)
    if post is None:
        return 'Not found', 404
    if current_user.is_anonymous:
        return 'Forbidden', 403
    if 'action' not in request.form:
        return 'Bad request', 400
    old_vote = Vote.query.filter(Vote.user == current_user, Vote.post == post).first()
    action = request.form['action']
    if action not in ['remove', 'upvote', 'downvote']:
        return 'Bad request', 400
    if old_vote:
        db.session.delete(old_vote)
        db.session.commit()
    if action == 'remove':
        vote = None
    elif action == 'upvote':
        vote = Vote(post=post, user=current_user, is_upvote=True)
    else:
        vote = Vote(post=post, user=current_user, is_upvote=False)
    if vote:
        db.session.add(vote)
        db.session.commit()
    url = url_for('main.post', post_id=post.top().id) + f'#post-{post.id}'
    return redirect(url)


