from server import db, create_app
from server.models import User,Item,Post, Comment

app = create_app()
app.app_context().push()

with app.app_context():
    db.create_all()


