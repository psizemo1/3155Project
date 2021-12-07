from flask import url_for
from flask_login import UserMixin
from sqlalchemy.orm import dynamic

from . import db

DEFAULT_USER_PICTURES = [
    "https://3155project.s3.amazonaws.com/profile-1.png",
    "https://3155project.s3.amazonaws.com/profile-2.png",
    "https://3155project.s3.amazonaws.com/profile-3.png",
    "https://3155project.s3.amazonaws.com/profile-4.png",
    "https://3155project.s3.amazonaws.com/profile-5.png",
    "https://3155project.s3.amazonaws.com/profile-6.png",
]

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    description = db.Column(db.String(1000))
    users = db.relationship('User', secondary='group_user', backref='groups')

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Group {self.name}>'


class GroupUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', backref=db.backref('images', lazy=True, cascade='all, delete-orphan'))
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def __str__(self):
        return f'Image {self.id}'

    def __repr__(self):
        return f'<Image {self.id}>'


class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('votes', lazy=True))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', backref=db.backref('votes', lazy=True))
    is_upvote = db.Column(db.Boolean)
    created_at = db.Column(db.DateTime, default=db.func.now())

    # Enforce unique vote per user per post
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='user_post_uc'),)

    def __str__(self):
        return f'Vote {self.id}'

    def __repr__(self):
        return f'<Vote {self.id}>'


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000))
    content = db.Column(db.String(10000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship('Group', backref=db.backref('posts', lazy=True))
    parent_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    parent = db.relationship('Post', remote_side=[id], backref=db.backref('children', lazy=True))
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def score(self):
        votes = Vote.query.filter_by(post_id=self.id)
        upvotes = votes.filter_by(is_upvote=True).count()
        downvotes = votes.filter_by(is_upvote=False).count()
        return upvotes - downvotes

    def top(self):
        cur = self
        while cur.parent:
            cur = cur.parent
        return cur

    @classmethod
    def search(cls, search_term):
        return sorted(cls.query.filter(cls.title.ilike('%' + search_term + '%')).filter_by(parent_id=None).all(),
                      key=lambda x: x.created_at, reverse=True)

    def __str__(self):
        if self.parent is None:
            return f'"{self.title}"'
        node = self
        while node.parent:
            node = node.parent
        return f'reply in {node}'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(10))
    password = db.Column(db.String(100))
    picture_id = db.Column(db.Integer, db.ForeignKey('user_image.id'), nullable=True)
    picture = db.relationship('UserImage', backref=db.backref('users', lazy=True))
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __init__(self, name, email, phone, password):
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password

        # Check if default group exists
        default_group = Group.query.filter_by(name='default').first()
        if default_group is None:
            default_group = Group(name='default')
            db.session.add(default_group)

        # Add user to default group
        default_group.users.append(self)

    def upvoted(self, post):
        return Vote.query.filter_by(user_id=self.id, post_id=post.id, is_upvote=True).first() is not None

    def downvoted(self, post):
        return Vote.query.filter_by(user_id=self.id, post_id=post.id, is_upvote=False).first() is not None

    def picture_url(self):
        if self.picture_id:
            return url_for("main.user_image", image_id=self.picture_id)
        else:
            return DEFAULT_USER_PICTURES[self.id % len(DEFAULT_USER_PICTURES)]


class UserImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.LargeBinary)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __init__(self, image):
        self.image = image

    def __str__(self):
        return f'UserImage {self.id}'

    def __repr__(self):
        return f'<UserImage {self.id}>'
