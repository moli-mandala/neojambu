"""
File: search.py
Description: Contains helper functions for filtering queries from the db based on various criteria.
Author: Aryaman Arora (aryaman.arora2020@gmail.com)
Date: 2023-05-19
"""

from models import Language, Lemma, Concept, Reference

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
    for i in filters:
        r = request.args.get(i, None)
        if r:
            query = filters[i](query, r, model)
    return query
