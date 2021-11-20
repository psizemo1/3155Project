import unittest

from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from . import db, create_app
from .models import User, Group, Post, GroupUser

SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

app = create_app()
app.config.from_object(__name__)
app.app_context().push()


class TestUser(unittest.TestCase):
    def setUp(self):
        self.engine = db.get_engine(app=app)
        self.session = Session(self.engine)
        db.create_all(app=app)

    def test_create(self):
        user = User(email='email', name='name', phone='phone',
                    password=generate_password_hash('password', method='sha256'))
        self.session.add(user)
        self.session.commit()
        self.assertEqual(user.email, 'email')
        self.assertEqual(user.name, 'name')
        self.assertEqual(user.phone, 'phone')

    def tearDown(self):
        db.drop_all(app=app)


class TestGroup(unittest.TestCase):
    def setUp(self):
        self.engine = db.get_engine(app=app)
        self.session = Session(self.engine)
        db.create_all(app=app)

    def test_create(self):
        group = Group(name='name', description='description')
        self.session.add(group)
        self.session.commit()
        self.assertEqual(group.name, 'name')
        self.assertEqual(group.description, 'description')

    def tearDown(self):
        db.drop_all(app=app)


class TestGroupUser(unittest.TestCase):
    def setUp(self):
        self.engine = db.get_engine(app=app)
        self.session = Session(self.engine)
        db.create_all(app=app)
        self.session.add(User(email='email', name='name', phone='phone'))
        self.session.add(Group(name='name', description='description'))
        self.session.commit()

    def test_create(self):
        group_user = GroupUser(group_id=1, user_id=1)
        self.session.add(group_user)
        self.session.commit()
        self.assertEqual(group_user.group_id, 1)
        self.assertEqual(group_user.user_id, 1)

    def tearDown(self):
        db.drop_all(app=app)


class TestPost(unittest.TestCase):
    def setUp(self):
        self.engine = db.get_engine(app=app)
        self.session = Session(self.engine)
        db.create_all(app=app)
        self.session.add(User(email='email', name='name', phone='phone'))
        self.session.add(Group(name='name', description='description'))
        self.session.commit()

    def test_create(self):
        post = Post(title='title', content='content', user_id=1, group_id=1)
        self.session.add(post)
        self.session.commit()
        self.assertEqual(post.title, 'title')
        self.assertEqual(post.content, 'content')
        self.assertEqual(post.user_id, 1)
        self.assertEqual(post.group_id, 1)

    def test_search(self):
        post1 = Post(title='Hello World', content='content', user_id=1, group_id=1)
        post2 = Post(title='Hi how are you', content='lol', user_id=1, group_id=1)
        post3 = Post(title='Hi I am fine', content='lol', user_id=1, group_id=1)
        for post in post1, post2, post3:
            self.session.add(post)
        self.session.commit()
        self.assertListEqual([p.id for p in Post.search('hello')], [post1.id])
        self.assertListEqual([p.id for p in Post.search('world')], [post1.id])
        self.assertListEqual([p.id for p in Post.search('fine')], [post3.id])
        self.assertListEqual([p.id for p in Post.search('HI')], [post2.id, post3.id])

    def tearDown(self):
        db.drop_all(app=app)


if __name__ == '__main__':
    unittest.main()
