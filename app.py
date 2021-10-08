from flask import Flask
from views import views

app = Flask(__name__)
# this allows routes to be stored in a separate file called views
app.register_blueprint(views, url_prefix="/")


if __name__ == '__main__':
    app.run();