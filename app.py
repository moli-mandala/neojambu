from flask import Flask, render_template, request, url_for
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, joinedload, Query
from sqlalchemy.orm.collections import InstrumentedList
from models import Language, Lemma, Concept, Reference
from make_database import colors
from markdown import markdown
from jinja2 import Environment
from itertools import groupby

from search import filter_data, filter_page

app = Flask(__name__)
app.jinja_env.filters["markdown"] = lambda text: markdown(text.replace("\\n", "\n\n"))

# load database with connection pooling
engine = create_engine(
    "sqlite:///data.db",
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={'check_same_thread': False}
)
Session = sessionmaker(bind=engine)

# Create session per request instead of global session
def get_session():
    return Session()
order = list(colors.keys())

@app.route("/")
def hello_world():
    return render_template("index.html", title="Home")


def serialise(query):
    if type(query) in [Query, list, InstrumentedList]:
        return [serialise(row) for row in query]
    else:
        result = query.__dict__
        if "_sa_instance_state" in result:
            del result["_sa_instance_state"]
        return result


@app.route("/query")
def query():
    query_type = request.args.get("type")

    # a single reflex
    if query_type == "reflex":
        reflex = request.args.get("reflex")
        session = get_session()
        lemma = session.query(Lemma).filter_by(id=reflex).first()
        result = serialise(lemma)
        session.close()
        return result

    # list of reflexes
    if query_type == "reflexes":
        session = get_session()
        lemmas, sort = filter_data(session.query(Lemma).join(Language), request, Lemma)
        lemmas = lemmas.order_by(Lemma.order, Language.clade, Language.name)
        lemmas = filter_page(lemmas, request)
        result = serialise(lemmas)
        session.close()
        return result

    # a single language's reflexes
    if query_type == "language":
        session = get_session()
        language = request.args.get("language")
        lang = session.query(Language).filter_by(id=language).first()
        lemmas = (
            session.query(Lemma)
            .filter_by(language_id=language)
            .options(joinedload(Lemma.origin_lemma))
            .join(Language)
        )
        lemmas, sort = filter_data(lemmas, request, Lemma)
        lemmas = lemmas.join(Lemma.origin_lemma, aliased=True).order_by(Lemma.order)
        lemmas = filter_page(lemmas, request)

        result = serialise(lemmas)
        for i in range(len(result)):
            result[i]["origin_lemma"] = serialise(result[i]["origin_lemma"])
        session.close()
        return result

    # all languages
    if query_type == "languages":
        session = get_session()
        langs = session.query(Language).order_by(Language.order, Language.name)
        langs, sort = filter_data(langs, request, Language)
        result = serialise(langs)
        session.close()
        return result

    # a single entry's reflexes
    if query_type == "entry":
        session = get_session()
        entry = request.args.get("entry")
        reflexes = (
            session.query(Lemma)
            .filter_by(origin_lemma_id=entry)
            .options(joinedload(Lemma.language), joinedload(Lemma.references))
        )
        reflexes, sort = filter_data(reflexes, request, Lemma)
        result = serialise(reflexes)
        for i in range(len(result)):
            result[i]["language"] = serialise(result[i]["language"])
            result[i]["references"] = serialise(result[i]["references"])
        session.close()
        return result

    # all entries
    if query_type == "entries":
        session = get_session()
        entries = (
            session.query(Lemma)
            .filter(Lemma.origin_lemma_id == None)
            .order_by(Lemma.order)
        )
        entries, sort = filter_data(entries.join(Language), request, Lemma)
        entries = filter_page(entries, request)
        result = serialise(entries)
        session.close()
        return result

    # single ref
    if query_type == "reference":
        session = get_session()
        reference = request.args.get("reference")
        source = session.query(Reference).filter_by(id=reference).first()
        result = serialise(source)
        session.close()
        return result

    # all refs
    if query_type == "references":
        session = get_session()
        sources = session.query(Reference)
        sources, sort = filter_data(sources, request, Reference)
        result = serialise(sources)
        session.close()
        return result


@app.route("/reflexes")
@app.route("/reflexes/<reflex>")
def reflexes(reflex=None):
    page = int(request.args.get("page", 1))
    if reflex:
        session = get_session()
        lemma = session.query(Lemma).options(
            joinedload(Lemma.language), 
            joinedload(Lemma.origin_lemma).joinedload(Lemma.language),
            joinedload(Lemma.references)
        ).filter_by(id=reflex).first()
        session.close()
        if lemma:
            return render_template(
                "reflex.html", reflex=lemma, title=f"Reflex {lemma.word} [{lemma.id}]"
            )
        return "Lemma not found"
    else:
        session = get_session()
        lemmas, sort = filter_data(session.query(Lemma).join(Language), request, Lemma)
        if sort:
            lemmas = lemmas.order_by(Lemma.order, Language.clade, Language.name)
        
        # Optimize: Get count first, then get page results
        count = lemmas.count()
        reflexes_list = lemmas.options(
            joinedload(Lemma.language), 
            joinedload(Lemma.origin_lemma).joinedload(Lemma.language),
            joinedload(Lemma.references)
        ).offset(page * 50 - 50).limit(50).all()
        session.close()
        
        return render_template(
            "reflexes.html",
            reflexes=reflexes_list,
            page=page,
            count=count,
            title="Reflexes",
        )


@app.route("/languages")
@app.route("/languages/<lang1>")
@app.route("/languages/<lang1>/<lang2>")
def languages(lang1=None, lang2=None):
    page = int(request.args.get("page", 1))
    if lang1 and lang2:
        session = get_session()
        lang1_data = (
            session.query(Lemma)
            .filter_by(language_id=lang1)
            .filter(Lemma.origin_lemma_id is not None)
            .join(Lemma.origin_lemma, aliased=True)
            .order_by(Lemma.order)
            .all()
        )
        lang2_data = (
            session.query(Lemma)
            .filter_by(language_id=lang2)
            .filter(Lemma.origin_lemma_id is not None)
            .join(Lemma.origin_lemma, aliased=True)
            .order_by(Lemma.order)
            .all()
        )
        lang1_data = [(x.origin_lemma_id, x) for x in lang1_data]
        lang2_data = [(x.origin_lemma_id, x) for x in lang2_data]
        lang1_dict, lang2_dict = {}, {}

        for i in lang1_data:
            if i[0] not in lang1_dict:
                lang1_dict[i[0]] = []
            lang1_dict[i[0]].append(i[1])
        for i in lang2_data:
            if i[0] not in lang2_dict:
                lang2_dict[i[0]] = []
            lang2_dict[i[0]].append(i[1])

        both = []
        for i in lang1_dict:
            if i in lang2_dict:
                both.append(i)

        lang1 = session.query(Language).filter_by(id=lang1).first()
        lang2 = session.query(Language).filter_by(id=lang2).first()
        session.close()

        if lang1 and lang2:
            return render_template(
                "compare.html",
                colors=colors,
                both=both,
                count=len(both),
                lang1=lang1,
                lang2=lang2,
                lang_dict=lang1_dict,
                lang2_dict=lang2_dict,
                title=f"Languages {lang1.name} vs {lang2.name}",
            )
        else:
            return "Language not found"

    elif lang1:
        page = int(request.args.get("page", 1))
        session = get_session()

        language = session.query(Language).filter_by(id=lang1).first()
        if language:
            lemmas = (
                session.query(Lemma)
                .filter_by(language_id=lang1)
                .options(joinedload(Lemma.origin_lemma))
            )
            lemmas, sort = filter_data(lemmas.join(Language), request, Lemma)
            if sort:
                lemmas = lemmas.order_by(Lemma.order)

            # Optimize: Get count first, then get page results
            count = lemmas.count()
            reflexes_list = lemmas.options(
            joinedload(Lemma.language), 
            joinedload(Lemma.origin_lemma).joinedload(Lemma.language),
            joinedload(Lemma.references)
        ).offset(page * 50 - 50).limit(50).all()
            session.close()

            return render_template(
                "reflexes.html",
                lang=language,
                colors=colors,
                count=count,
                reflexes=reflexes_list,
                page=page,
                title=f"Language {language.name}",
            )
        else:
            session.close()
            return "Language not found"

    elif lang2:
        return "Wut did you do"

    else:
        session = get_session()
        langs = session.query(Language)
        langs, sort = filter_data(langs, request, Language)
        if sort:
            langs = langs.order_by(Language.order, Language.name)
        
        langs_list = langs.all()
        count = langs.count()
        session.close()
        
        return render_template(
            "langs.html",
            langs=langs_list,
            count=count,
            colors=colors,
            title="Languages",
        )


@app.route("/entries")
@app.route("/entries/<entry>")
def entries(entry=None, lang=None):
    page = int(request.args.get("page", 1))
    if entry:
        session = get_session()
        entry_info = session.query(Lemma).options(joinedload(Lemma.language)).filter_by(id=entry).first()
        if entry_info:
            reflexes_query = session.query(Lemma).filter_by(origin_lemma_id=entry).join(Language)
            total_count = reflexes_query.count()
            reflexes_query, sort = filter_data(
                reflexes_query,
                request,
                Lemma,
            )
            count = reflexes_query.count()

            # group reflexes by cognate set first (i.e. subgroup)
            if sort:
                reflexes_cognatesets = reflexes_query.options(
                    joinedload(Lemma.language),
                    joinedload(Lemma.references)
                ).order_by(Lemma.cognateset).all()
            else:
                reflexes_cognatesets = reflexes_query.options(
                    joinedload(Lemma.language),
                    joinedload(Lemma.references)
                ).all()
            grouped_cognatesets = [
                [key, list(group)]
                for key, group in groupby(
                    reflexes_cognatesets, key=lambda lemma: lemma.cognateset if sort else None
                )
            ]
            if sort:
                grouped_cognatesets.sort(key=lambda x: x[1][0].id)

            # subgroup each cognateset by language
            for i in range(len(grouped_cognatesets)):
                if sort:
                    grouped_cognatesets[i][1].sort(
                        key=lambda x: (x.language.order, x.language.name)
                    )
                grouped_cognatesets[i][1] = [
                    (key, list(group))
                    for key, group in groupby(
                        grouped_cognatesets[i][1], key=lambda lemma: lemma.language
                    )
                ]

            # by langs separately (for dots on map)
            reflexes_langs = reflexes_query.options(
                joinedload(Lemma.language),
                joinedload(Lemma.references)
            ).order_by(
                Language.order, Language.name
            ).all()
            grouped_langs = {
                key: list(group)
                for key, group in groupby(
                    reflexes_langs, key=lambda lemma: lemma.language
                )
            }
            session.close()

            return render_template(
                "entry.html",
                entry=entry_info,
                reflexes=grouped_cognatesets,
                grouped_langs=grouped_langs,
                colors=colors,
                order=order,
                title=f"Entry {entry_info.word}",
                count=count,
                total_count=total_count,
            )
        else:
            session.close()
            return "Entry not found"
    else:
        session = get_session()
        entries_query = (
            session.query(Lemma)
            .filter(Lemma.origin_lemma_id == None)
            .options(joinedload(Lemma.language))  # Eagerly load language relationship
        )
        entries, sort = filter_data(entries_query.join(Language), request, Lemma)
        if sort:
            entries = entries.order_by(Lemma.order)
        
        # Optimize: Get count first, then get page results
        count = entries.count()
        entries_list = entries.offset(page * 50 - 50).limit(50).all()
        session.close()
        
        return render_template(
            "entries.html",
            entries=entries_list,
            count=count,
            page=page,
            colors=colors,
            order=order,
            title="Entries",
        )


@app.route("/references")
@app.route("/references/<ref>")
def references(ref=None):
    if ref:
        session = get_session()
        source = session.query(Reference).filter_by(id=ref).first()
        session.close()
        if source:
            return render_template(
                "reference.html",
                source=source,
                title=f"Source {source.short} [{source.id}]",
            )
        else:
            return "Source not found"
    else:
        session = get_session()
        refs = session.query(Reference).all()
        session.close()
        return render_template("references.html", sources=refs, title="Sources")


if __name__ == "__main__":
    app.run(threaded=True, port=2222)
