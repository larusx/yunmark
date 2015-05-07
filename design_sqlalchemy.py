from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root@localhost/test'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=1)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(50))
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, password, email=None):
        self.username = username
        self.password = password
        self.email = email



class Content(db.Model):
    id = db.Column(db.Integer)
    tag = db.Column(db.String(200))
    hash = db.Column(db.String(100), primary_key=True)
    original = db.Column(db.Text)
    text = db.Column(db.Text)
    doneStatus = db.Column(db.Boolean, default=False)
    shareStatus = db.Column(db.Boolean, default=False)
    existStatus = db.Column(db.Boolean, default=True)

    def __init__(self, id, tag, hash, original, text):
        self.id = id
        self.tag = tag
        self.hash = hash
        self.original = original
        self.text = text


db.drop_all()
db.create_all()
content = Content(3,'23','22','33','22')
db.session.add(content)
content = Content(3,'23','23','33','22')
db.session.add(content)
content = Content(3,'23','25','33','22')
db.session.add(content)
db.session.commit()

ret = Content.query.filter_by(id=3).all()
print json.dumps(ret)