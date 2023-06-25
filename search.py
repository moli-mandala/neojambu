"""
File: search.py
Description: Contains helper functions for filtering queries from the db based on various criteria.
Author: Aryaman Arora (aryaman.arora2020@gmail.com)
Date: 2023-05-19
"""

from models import Language, Lemma, Concept, Reference

sort = {
    "lang": Language.name,
    "word": Lemma.word,
    "gloss": Lemma.gloss,
    "notes": Lemma.notes,
    "source": Reference.short,
    "origin": Lemma.word,
    "clade": Language.clade,
}

filters = {
    "lang": lambda x, y, z: x.filter(Language.name.like("%" + y + "%")),
    "word": lambda x, y, z: x.filter(Lemma.word.like("%" + y + "%")),
    "gloss": lambda x, y, z: x.filter(Lemma.gloss.like("%" + y + "%")),
    "notes": lambda x, y, z: x.filter(Lemma.notes.like("%" + y + "%")),
    "source": lambda x, y, z: x.join(Lemma.references).filter(
        Reference.short.like("%" + y + "%")
    ),
    "origin_lang": lambda x, y, z: x.join(Lemma.origin_lemma, aliased=True).filter(
        Lemma.language_id == y
    ),
    "origin": lambda x, y, z: x.join(Lemma.origin_lemma, aliased=True).filter(
        Lemma.word.like("%" + y + "%")
    ),
    "clade": lambda x, y, z: x.filter(Language.clade.like("%" + y + "%")),
}


def filter_data(query, request, model):
    # sort
    order, col = None, None
    s = request.args.get("sort", None)
    if s:
        order, col = s.split("_")

    # filter
    for i in filters:
        r = request.args.get(i, None)
        if r:
            query = filters[i](query, r, model)
        if col == i and col in sort:
            if order == "asc":
                query = query.order_by(sort[col])
            elif order == "desc":
                query = query.order_by(sort[col].desc())

    return query
