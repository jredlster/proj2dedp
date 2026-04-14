
from FlaskWebProject import app, db
from FlaskWebProject.models import User, Post

with app.app_context():
    db.create_all()

