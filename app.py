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

# load database
engine = create_engine("sqlite:///data.db")  # Use your own database URL here
Session = sessionmaker(bind=engine)
session = Session()
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
        lemma = session.query(Lemma).filter_by(id=reflex).first()
        return serialise(lemma)

    # list of reflexes
    if query_type == "reflexes":
        lemmas, sort = filter_data(session.query(Lemma).join(Language), request, Lemma)
        lemmas = lemmas.order_by(Lemma.order, Language.clade, Language.name)
        lemmas = filter_page(lemmas, request)
        return serialise(lemmas)

    # a single language's reflexes
    if query_type == "language":
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
        return result

    # all languages
    if query_type == "languages":
        langs = session.query(Language).order_by(Language.order, Language.name)
        langs, sort = filter_data(langs, request, Language)
        return serialise(langs)

    # a single entry's reflexes
    if query_type == "entry":
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
        return result

    # all entries
    if query_type == "entries":
        entries = (
            session.query(Lemma)
            .filter(Lemma.origin_lemma_id == None)
            .order_by(Lemma.order)
        )
        entries, sort = filter_data(entries.join(Language), request, Lemma)
        entries = filter_page(entries, request)
        return serialise(entries)

    # single ref
    if query_type == "reference":
        reference = request.args.get("reference")
        source = session.query(Reference).filter_by(id=reference).first()
        return serialise(source)

    # all refs
    if query_type == "references":
        sources = session.query(Reference)
        sources, sort = filter_data(sources, request, Reference)
        return serialise(sources)


@app.route("/reflexes")
@app.route("/reflexes/<reflex>")
def reflexes(reflex=None):
    page = int(request.args.get("page", 1))
    if reflex:
        lemma = session.query(Lemma).filter_by(id=reflex).first()
        if lemma:
            return render_template(
                "reflex.html", reflex=lemma, title=f"Reflex {lemma.word} [{lemma.id}]"
            )
        return "Lemma not found"
    else:
        lemmas, sort = filter_data(session.query(Lemma).join(Language), request, Lemma)
        if sort:
            lemmas = lemmas.order_by(Lemma.order, Language.clade, Language.name)
        return render_template(
            "reflexes.html",
            reflexes=lemmas.limit(50).offset(page * 50 - 50).all(),
            page=page,
            count=lemmas.count(),
            title="Reflexes",
        )


@app.route("/languages")
@app.route("/languages/<lang1>")
@app.route("/languages/<lang1>/<lang2>")
def languages(lang1=None, lang2=None):
    page = int(request.args.get("page", 1))
    if lang1 and lang2:
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

            return render_template(
                "reflexes.html",
                lang=language,
                colors=colors,
                count=lemmas.count(),
                reflexes=lemmas
                .limit(50)
                .offset(page * 50 - 50)
                .all(),
                page=page,
                title=f"Language {language.name}",
            )
        else:
            return "Language not found"

    elif lang2:
        return "Wut did you do"

    else:
        langs = session.query(Language)
        langs, sort = filter_data(langs, request, Language)
        if sort:
            langs = langs.order_by(Language.order, Language.name)
        return render_template(
            "langs.html",
            langs=langs.all(),
            count=langs.count(),
            colors=colors,
            title="Languages",
        )


@app.route("/entries")
@app.route("/entries/<entry>")
def entries(entry=None, lang=None):
    page = int(request.args.get("page", 1))
    if entry:
        entry_info = session.query(Lemma).filter_by(id=entry).first()
        if entry_info:
            reflexes_query, sort = filter_data(
                session.query(Lemma).filter_by(origin_lemma_id=entry).join(Language),
                request,
                Lemma,
            )

            # group reflexes by cognate set first (i.e. subgroup)
            if sort:
                reflexes_cognatesets = reflexes_query.order_by(Lemma.cognateset).all()
            else:
                reflexes_cognatesets = reflexes_query.all()
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
            reflexes_langs = reflexes_query.order_by(
                Language.order, Language.name
            ).all()
            grouped_langs = {
                key: list(group)
                for key, group in groupby(
                    reflexes_langs, key=lambda lemma: lemma.language
                )
            }

            return render_template(
                "entry.html",
                entry=entry_info,
                reflexes=grouped_cognatesets,
                grouped_langs=grouped_langs,
                colors=colors,
                order=order,
                title=f"Entry {entry_info.word}",
            )
        else:
            return "Entry not found"
    else:
        entries_query = (
            session.query(Lemma)
            .filter(Lemma.origin_lemma_id == None)
        )
        entries, sort = filter_data(entries_query.join(Language), request, Lemma)
        if sort:
            entries = entries.order_by(Lemma.order)
        return render_template(
            "entries.html",
            entries=entries.limit(50).offset(page * 50 - 50).all(),
            count=entries.count(),
            page=page,
            colors=colors,
            order=order,
            title="Entries",
        )


@app.route("/references")
@app.route("/references/<ref>")
def references(ref=None):
    if ref:
        source = session.query(Reference).filter_by(id=ref).first()
        if source:
            return render_template(
                "reference.html",
                source=source,
                title=f"Source {source.short} [{source.id}]",
            )
        else:
            return "Source not found"
    else:
        refs = session.query(Reference).all()
        return render_template("references.html", sources=refs, title="Sources")


if __name__ == "__main__":
    app.run(threaded=True, port=2222)
