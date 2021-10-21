from qa import db, create_app, models

if __name__ == '__main__':
    _ = models
    db.create_all(app=create_app())
