from flask import Blueprint, render_template
from .models import User, Note
from . import db
from flask_login import  current_user
import pickle

news = Blueprint('news', __name__)
PATH_TO_MODEL = 'website/model.pickle'


@news.route("/news")
def show_news():
    public_notes = db.session.query(Note, User).filter(User.id == Note.user_id).filter_by(is_public=True)
    recommender = pickle.load(open(PATH_TO_MODEL, 'rb'))
    recommendations_note_ids = recommender.recommend(current_user.id)
    recommended_notes = db.session.query(Note, User).filter(Note.id.in_(recommendations_note_ids)).filter(User.id == Note.user_id)

    return render_template('news.html', user=current_user, public_notes=public_notes, recommended_notes=recommended_notes)
