from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from qa import db, create_app
from qa.models import Post, User, Group


def main():
    engine = db.get_engine(app=create_app())
    session = Session(engine)
    user = User(email='mark@uncc.edu', username='Mark Smith', phone='123-456-7890',
                password=generate_password_hash('password', method='sha256'))
    group = Group(name='ITSC-3155', description='202180-Fall 2021-ITSC-3155-102-Software Engineering')
    group.users.append(user)
    post1 = Post(title='Help with activities for this week', content="""\
Hi, I'm Mark, and I'm in need of help with activities for this week.

My group is in need of help with the following:
- Creating a new project
- Creating a new class
- Creating a new method
- Creating a new test
- Creating a new test case

Thanks in advance for your help!
""", user=user, group=group)
    post2 = Post(title="Answers to test 1 questions", content="""\
Hey all, does anyone have the answers to the questions from test 1?

Thanks so much!
""", user=user, group=group)
    post3 = Post(title="Answers to test 2 questions", content="""\
Hey all, does anyone have the answers to the questions from test 2?

Thank you so much!""", user=user, group=group)

    for obj in user, group, post1, post2, post3:
        session.add(obj)
        session.commit()
    session.close()


if __name__ == '__main__':
    main()
