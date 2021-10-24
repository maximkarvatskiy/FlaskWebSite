from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

subs = db.Table('subs',
                db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                db.Column('note_id', db.Integer, db.ForeignKey('note.id')))


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    is_public = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    notes = db.relationship('Note')
    subscriptions = db.relationship('Note', secondary=subs, backref=db.backref('subscribers', lazy='dynamic'),
                                    cascade="all, delete", passive_deletes=True)
