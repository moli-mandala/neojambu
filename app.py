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

    lang_filter = request.args.get('lang', None)
    word_filter = request.args.get('word', None)
    gloss_filter = request.args.get('gloss', None)
    source_filter = request.args.get('source', None)
    origin_filter = request.args.get('origin', None)

    if reflex:
        lemma = session.query(Lemma).filter_by(id=reflex).first()
        return render_template('reflex.html', reflex=lemma)
    else:
        page = int(request.args.get('page', 1))
        lemmas = session.query(Lemma)

        if lang_filter:
            lemmas = lemmas.join(Language).filter(Language.name.like('%' + lang_filter + '%'))
        if word_filter:
            lemmas = lemmas.filter(Lemma.word.like('%' + word_filter + '%'))
        if gloss_filter:
            lemmas = lemmas.filter(Lemma.gloss.like('%' + gloss_filter + '%'))
        if source_filter:
            lemmas = lemmas.join(Lemma.references).filter(Reference.short.like('%' + source_filter + '%'))
        if origin_filter:
            lemmas = lemmas.join(Lemma.origin_lemma, aliased=True).filter(Lemma.word.like('%' + origin_filter + '%'))
            
        return render_template(
            'reflexes.html',
            reflexes=lemmas.limit(50).offset(page * 50 - 50).all(),
            page=page,
            count=lemmas.count(),
        )

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

        return render_template('compare.html', colors=colors, both=both, count=len(both), lang1=lang1, lang2=lang2, lang_dict=lang1_dict, lang2_dict=lang2_dict)

    elif lang1:
        page = int(request.args.get('page', 1))

        language = session.query(Language).filter_by(id=lang1).first()
        lemmas = session.query(Lemma).filter_by(language_id=lang1).options(joinedload(Lemma.origin_lemma))

        return render_template('reflexes.html', lang=language, colors=colors, count=lemmas.count(), reflexes=lemmas.limit(50).offset(page * 50 - 50).all(), page=page)
    
    else:
        lang_filter = request.args.get('lang', None)
        clade_filter = request.args.get('clade', None)
        langs = session.query(Language).order_by(Language.order)
        if lang_filter:
            langs = langs.filter(Language.name.like('%' + lang_filter + '%'))
        if clade_filter:
            langs = langs.filter(Language.clade.like('%' + clade_filter + '%'))
        return render_template('langs.html', langs=langs.all(), count=langs.count(), colors=colors)

@app.route("/entries")
@app.route('/entries/<entry>')
def entries(entry=None, lang=None):
    page = int(request.args.get('page', 1))
    search = request.args.get('entry', None)
    lang_filter = request.args.get('lang', None)
    entry_filter = request.args.get('entry_name', None)
    source_filter = request.args.get('source', None)
    gloss_filter = request.args.get('gloss', None)
    if entry:
        entry_info = session.query(Lemma).filter_by(id=entry).first()
        reflexes_query = session.query(Lemma).filter_by(origin_lemma_id=entry)
        if lang_filter:
            reflexes_query = reflexes_query.filter_by(language_id=lang_filter)
        if entry_filter:
            reflexes_query = reflexes_query.filter(Lemma.word.like('%' + entry_filter + '%'))
        if gloss_filter:
            reflexes_query = reflexes_query.filter(Lemma.gloss.like('%' + gloss_filter + '%'))
        reflexes = reflexes_query.join(Language).order_by(Language.order).all()
        grouped_reflexes = {key: list(group) for key, group in groupby(reflexes, key=lambda lemma: lemma.language_id)}
        return render_template('entry.html', entry=entry_info, reflexes=grouped_reflexes, colors=colors, order=order)
    else:
        entries_query = session.query(Lemma).filter(Lemma.origin_lemma_id == None)
        if lang_filter:
            entries_query = entries_query.filter_by(language_id=lang_filter)
        if entry_filter:
            entries_query = entries_query.filter(Lemma.word.like('%' + entry_filter + '%'))
        entries = entries_query
        return render_template('entries.html', entries=entries.limit(50).offset(page * 50 - 50).all(), count=entries.count(), page=page, colors=colors, order=order)

@app.route("/references")
def references():
    refs = session.query(Reference).all()
    return render_template('references.html', sources=refs)

if __name__ == '__main__':
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=2222, debug=True)