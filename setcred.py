
from FlaskWebProject import app, db
from FlaskWebProject.models import User

with app.app_context():
    user = User(username="admin")
    user.set_password("admin")  # use your model’s password method
    db.session.add(user)
    db.session.commit()
