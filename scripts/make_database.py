from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.neojambu.models import Language, Lemma, Reference, Concept, Base
from typing import List
import pybtex.database
import pybtex.bibtex

import os
import csv
from tqdm import tqdm
from collections import defaultdict

colors = {
    "OIA": "E2DFD2",
    "MIA": "FFDEAD",
    "Migratory": "63666A",
    "Nuristani": "9132a8",
    "Pashai": "FFD6F6",
    "Chitrali": "FFACEF",
    "Shinaic": "FF81E6",
    "Kohistani": "FF25D5",
    "Kunar": "ff68e0",
    "Kashmiric": "FF00CD",
    "Sindhic": "0066FF",
    "Lahndic": "a4d6f5",
    "Punjabic": "7164FF",
    "W. Pahari": "B94E16",
    "C. Pahari": "9E521B",
    "E. Pahari": "79421B",
    "Eastern": "FFDE54",
    "Bihari": "FFCD00",
    "E. Hindi": "FF9A54",
    "W. Hindi": "FF6600",
    "Rajasthanic": "6BCD00",
    "Gujaratic": "00CF4A",
    "Marathi-Konkani": "D50000",
    "Bhil": "09AD02",
    "Khandeshi": "2FFF2F",
    "Halbic": "AB8900",
    "Insular": "AC0000",
    "Old Dravidian": "679267",
    "S. Dravidian I": "74C365",
    "S. Dravidian II": "98FB98",
    "C. Dravidian": "29AB87",
    "N. Dravidian": "4B6F44",
    "Brahui": "49796B",
    "Munda": "00ffd0",
    "Burushaski": "f3ff05",
    "Nihali": "ff9a00",
    "Other": "FAF9F6",
}
order = list(colors.keys())


def parse_ref(ref: str) -> List[str]:
    """parses references of the forms 'ref1:page1;ref2:page2' with pages being optional"""
    if ref == "":
        return []
    return list(set([r.split("[")[0] for r in ref.split(";")]))


def create_short_ref(entry):
    year = entry.fields.get("year")
    authors = entry.persons.get("author", [])
    if year == "n.d.":
        year = "?"
    if authors and year:
        first_author = authors[0]
        first_letter = (
            first_author.last_names[0][0].upper()
            if first_author.last_names
            else first_author.first()[0].upper()
        )
        year = year.replace("--", "—")
        return f"{first_letter}{year}"
    else:
        return "?"


def main():
    # create engine and session
    if os.path.exists("data.db"):
        os.remove("data.db")
    engine = create_engine("sqlite:///data.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    # create all tables
    Base.metadata.create_all(engine)

    # format sources into html
    sources = pybtex.database.parse_file("../data/cldf/sources.bib")
    engine = pybtex.PybtexEngine()
    used_short = set()
    refs = {}
    for source in tqdm(sources.entries):
        try:
            formatted = engine.format_from_string(
                sources.entries[source].to_string("bibtex"),
                "plain",
                output_backend="markdown",
            )
            formatted = formatted[3:].strip()
        except Exception as e:
            print(e)
            formatted = ""

        short = create_short_ref(sources.entries[source])

        while short in used_short and short != "?":
            if short[-1].isdigit() or short[-1] == "?":
                short += "a"
            else:
                short = short[:-1] + chr(ord(short[-1]) + 1)
        used_short.add(short)
        reference = Reference(
            id=source,
            short=short,
            source=formatted,
            progress=sources.entries[source].fields.get("included", "No"),
        )
        refs[source] = reference
        session.add(reference)

    # languages
    clades = {}
    langs = {}
    with open("../data/cldf/languages.csv", "r") as f:
        lines = f.readlines()
        reader = csv.DictReader(lines)
        for row in tqdm(reader, total=len(lines)):
            language, dialect = row["Name"].split(": ") if ": " in row["Name"] else (row["Name"], "")
            marker = ""
            if row["Clade"] in ["MIA", "OIA"] or "Old" in row["Name"] or "Proto" in row["Name"]:
                marker = f"""<svg viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg"><polygon points="0,15 15,0 30,15 15,30" fill="#{colors[row['Clade']]}" stroke="black" stroke-width="2"/></svg>"""
            else:
                marker = f"""<svg viewBox="-2 -2 32 32" xmlns="http://www.w3.org/2000/svg"><circle cx="14" cy="14" r="13" fill="#{colors[row['Clade']]}" stroke="black" stroke-width="2"/></svg>"""
            language = Language(
                id=row["ID"],
                name=row["Name"],
                language=language,
                dialect=dialect,
                glottocode=row["Glottocode"],
                long=row["Longitude"],
                lat=row["Latitude"],
                clade=row["Clade"],
                color=colors[row["Clade"]],
                order=order.index(row["Clade"]),
                map_marker=marker,
            )
            clades[row["ID"]] = row["Clade"]
            langs[row["ID"]] = language
            session.add(language)

    # parameters
    lemma_cts = defaultdict(int)
    params = {}
    ordering = 0
    with open("../data/cldf/parameters.csv", "r") as f:
        lines = f.readlines()
        reader = csv.DictReader(lines)
        for i, row in enumerate(tqdm(reader, total=len(lines))):
            iden = row["ID"]
            parameter = Lemma(
                id=iden,
                word=row["Name"],
                gloss=row["Description"],
                language_id=row["Language_ID"],
                notes=row["Etyma"],
                order=ordering * 1000,
            )
            ordering += 1
            params[iden] = parameter
            session.add(parameter)

            # language ct
            lemma_cts[row["Language_ID"]] += 1

    # lemmata
    param_clades = defaultdict(set)
    param_cts = defaultdict(int)
    with open("../data/cldf/forms.csv", "r") as f:
        lines = f.readlines()
        reader = csv.DictReader(lines)
        for i, row in enumerate(tqdm(reader, total=len(lines))):
            # parse borrowing/semi-tatsama in parameter
            relation = "i"
            if row["Parameter_ID"][0] == ">":
                row["Parameter_ID"] = row["Parameter_ID"][1:]
                relation = "b"
            elif row["Parameter_ID"][0] == "~":
                row["Parameter_ID"] = row["Parameter_ID"][1:]
                relation = "s"

            # make lemma
            param_cts[row["Parameter_ID"]] += 1
            lemma = Lemma(
                id=row["ID"],
                word=row["Form"],
                gloss=row["Gloss"],
                native=row["Native"],
                phonemic=row["Phonemic"],
                original=row["Original"],
                notes=row["Description"],
                language_id=row["Language_ID"],
                origin_lemma_id=row["Parameter_ID"],
                cognateset=row["Cognateset"],
                relation=relation,
                order=params[row["Parameter_ID"]].order + param_cts[row["Parameter_ID"]],
            )

            # language ct
            lemma_cts[row["Language_ID"]] += 1

            # clade
            param_clades[row["Parameter_ID"]].add(clades[row["Language_ID"]])

            # add refs
            for ref in parse_ref(row["Source"]):
                reference = refs.get(ref, None)
                if reference is None:
                    reference = Reference(id=ref)
                    session.add(reference)
                lemma.references.append(reference)

            session.add(lemma)

    # update language lemma counts
    for language_id, ct in tqdm(lemma_cts.items()):
        language = langs[language_id]
        if language:
            language.lemma_count = ct

    for param_id, clades in tqdm(param_clades.items()):
        lemma = params[param_id]
        lemma.clades = ",".join(list(clades))

    session.commit()


if __name__ == "__main__":
    main()

