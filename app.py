from flask import Flask, render_template, request, url_for
import sqlite3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from models import Language, Lemma, Concept, Reference
from make_database import colors
from markdown import markdown
from jinja2 import Environment
from itertools import groupby

app = Flask(__name__)
app.jinja_env.filters['markdown'] = lambda text: markdown(text.replace('\\n', '\n\n'))

# load database
engine = create_engine('sqlite:///data.db')  # Use your own database URL here
Session = sessionmaker(bind=engine)
session = Session()
order = list(colors.keys())

@app.route("/")
def hello_world():
    return render_template('index.html')

@app.route("/reflexes")
@app.route("/reflexes/<reflex>")
def reflexes(reflex=None):
    con = sqlite3.connect('data.db')
    cur = con.cursor()
    if reflex:
        lemma = session.query(Lemma).filter_by(id=reflex).first()
        return render_template('reflex.html', reflex=lemma)
    else:
        page = int(request.args.get('page', 1))
        lemmas = session.query(Lemma).limit(200).offset(page * 200 - 200).all()
        return render_template('reflexes.html', reflexes=lemmas, page=page)

@app.route("/languages")
@app.route("/languages/<lang1>")
@app.route("/languages/<lang1>/<lang2>")
def languages(lang1=None, lang2=None):
    if lang1 and lang2:
        page = int(request.args.get('page', 1))

        lang1_data = session.query(Lemma).filter_by(language_id=lang1).filter(Lemma.origin_lemma_id is not None).all()
        lang2_data = session.query(Lemma).filter_by(language_id=lang2).filter(Lemma.origin_lemma_id is not None).all()

        lang1_data = [(x.origin_lemma_id, x) for x in lang1_data]
        lang2_data = [(x.origin_lemma_id, x) for x in lang2_data]
        lang1_dict, lang2_dict = {}, {}

        for i in lang1_data:
            if i[0] not in lang1_dict: lang1_dict[i[0]] = []
            lang1_dict[i[0]].append(i[1])
        for i in lang2_data:
            if i[0] not in lang2_dict: lang2_dict[i[0]] = []
            lang2_dict[i[0]].append(i[1])

        both = []
        for i in lang1_dict:
            if i in lang2_dict:
                both.append(i)

        lang1 = session.query(Language).filter_by(id=lang1).first()
        lang2 = session.query(Language).filter_by(id=lang2).first()

        return render_template('compare.html', colors=colors, both=both, lang1=lang1, lang2=lang2, lang_dict=lang1_dict, lang2_dict=lang2_dict)

    elif lang1:
        page = int(request.args.get('page', 1))
        language = session.query(Language).filter_by(id=lang1).first()
        lemmas = session.query(Lemma).filter_by(language_id=lang1).options(joinedload(Lemma.origin_lemma)).limit(50).all()
        return render_template('reflexes.html', lang=language, colors=colors, reflexes=lemmas, page=page)
    else:
        langs = session.query(Language).order_by(Language.order).all()
        return render_template('langs.html', langs=langs, colors=colors)

@app.route("/entries")
@app.route('/entries/<entry>')
def entries(entry=None, lang=None):
    page = int(request.args.get('page', 1))
    search = request.args.get('entry', None)
    if entry:
        entry_info = session.query(Lemma).filter_by(id=entry).first()
        reflexes = session.query(Lemma).filter_by(origin_lemma_id=entry).join(Language).order_by(Language.order).all()
        grouped_reflexes = {key: list(group) for key, group in groupby(reflexes, key=lambda lemma: lemma.language_id)}
        return render_template('entry.html', entry=entry_info, reflexes=grouped_reflexes, colors=colors, order=order)
    else:
        entries = session.query(Lemma).filter(Lemma.origin_lemma_id == None).limit(50).all()
        return render_template('entries.html', entries=entries, page=page, colors=colors, order=order)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=2222, debug=True)