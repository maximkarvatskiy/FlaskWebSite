from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User, Note
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
news = Blueprint('news', __name__)
import pickle
import os

from matrix_factorization import KernelMF, train_update_test_split
import itertools
import pickle
import pandas as pd
from .recomender_system_training import Recommender

@news.route("/news")
def show_news():
    public_notes = db.session.query(Note, User).filter(User.id == Note.user_id).filter_by(is_public=True)
    recommender = pickle.load(open('website/recommender.pickle', 'rb'))
    recomendation_note_ids = recommender.recommend(current_user.id)
    recommended_notes = db.session.query(Note, User).filter(Note.id.in_(recomendation_note_ids)).filter(User.id == Note.user_id)

    return render_template('news.html', user=current_user, public_notes=public_notes ,recommended_notes=recommended_notes)
