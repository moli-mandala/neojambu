"""
File: search.py
Description: Contains helper functions for filtering queries from the db based on various criteria.
Author: Aryaman Arora (aryaman.arora2020@gmail.com)
Date: 2023-05-19
"""

from models import Language, Lemma, Concept, Reference

filters = {
    "lang": lambda x, y: x.join(Language).filter(Language.name.like("%" + y + "%")),
    "word": lambda x, y: x.filter(Lemma.word.like("%" + y + "%")),
    "gloss": lambda x, y: x.filter(Lemma.gloss.like("%" + y + "%")),
    "source": lambda x, y: x.join(Lemma.references).filter(
        Reference.short.like("%" + y + "%")
    ),
    "origin": lambda x, y: x.join(Lemma.origin_lemma, aliased=True).filter(
        Lemma.word.like("%" + y + "%")
    ),
    "clade": lambda x, y: x.filter(Language.clade.like("%" + y + "%")),
}


def filter_data(query, request):
    for i in filters:
        if request.args.get(i, None):
            query = filters[i](query, request.args.get(i, None))
    return query
