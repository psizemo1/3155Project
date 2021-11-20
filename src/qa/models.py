from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(1000))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.String(10))
    password = db.Column(db.String(100))
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
