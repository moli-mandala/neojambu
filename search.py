"""
File: search.py
Description: Contains helper functions for filtering queries from the db based on various criteria.
Author: Aryaman Arora (aryaman.arora2020@gmail.com)
Date: 2023-05-19
"""

from models import Language, Lemma, Concept, Reference

joins = {
    "source": lambda x: x.join(Lemma.references),
    "origin_lang": lambda x: x.outerjoin(Lemma.origin_lemma, aliased=True),
    "origin": lambda x: x.outerjoin(Lemma.origin_lemma, aliased=True),
}

sorts = {
    "lang": Language.name,
    "word": Lemma.word,
    "gloss": Lemma.gloss,
    "notes": Lemma.notes,
    "source": Reference.short,
    "origin": Lemma.order,
    "clade": Language.clade,
    "reflexes": Language.lemma_count
}

filters = {
    "lang": lambda x, y, z: x.filter(Language.name.like("%" + y + "%")),
    "word": lambda x, y, z: x.filter(Lemma.word.like("%" + y + "%")),
    "gloss": lambda x, y, z: x.filter(Lemma.gloss.like("%" + y + "%")),
    "notes": lambda x, y, z: x.filter(Lemma.notes.like("%" + y + "%")),
    "source": lambda x, y, z: x.filter(Reference.short.like("%" + y + "%")),
    "origin_lang": lambda x, y, z: x.filter(Lemma.language_id == y),
    "origin": lambda x, y, z: x.filter(Lemma.word.like("%" + y + "%")),
    "clade": lambda x, y, z: x.filter(Language.clade.like("%" + y + "%")),
    "reflexes": lambda x, y, z: x
}


def filter_data(query, request, model):
    # sort
    order, col = None, None
    s = request.args.get("sort", None)
    if s:
        order, col = s.split("-")

    # filter
    for i in filters:
        r = request.args.get(i, None)
        if (r or (col == i and col in sorts)) and i in joins:
            query = joins[i](query)
        if r:
            query = filters[i](query, r, model)
        if col == i and col in sorts:
            if order == "asc":
                query = query.order_by(sorts[col])
            elif order == "desc":
                query = query.order_by(sorts[col].desc())
    
    return query, s is None or s == ""


def filter_page(query, request):
    page = int(request.args.get("page"))
    return query.limit(50).offset(int(page) * 50 - 50).all()
