from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker, relationship, backref, aliased
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Language(Base):
    __tablename__ = "languages"

    id = Column(String, primary_key=True)
    name = Column(String)
    language = Column(String)
    dialect = Column(String)
    glottocode = Column(String)
    long = Column(Float)
    lat = Column(Float)
    clade = Column(String)
    color = Column(String)
    lemma_count = Column(Integer, default=0)
    order = Column(Integer)
    map_marker = Column(String)

    def __repr__(self):
        return f"<Language(id='{self.id}', name='{self.name}', glottocode='{self.glottocode}', long={self.long}, lat={self.lat}, clade='{self.clade}', color='{self.color}')>"


class Concept(Base):
    __tablename__ = "concepts"

    id = Column(Integer, primary_key=True)
    meaning = Column(String)


class Reference(Base):
    __tablename__ = "references"

    id = Column(String, primary_key=True)
    short = Column(String)
    source = Column(String)
    progress = Column(String)

    def __repr__(self):
        return f'<a href="/references/{self.id}">{self.short}</a>'


class Lemma(Base):
    __tablename__ = "lemmas"

    id = Column(String, primary_key=True)
    word = Column(String)
    gloss = Column(String)
    native = Column(String)
    phonemic = Column(String)
    original = Column(String)
    notes = Column(String)
    clades = Column(String)
    cognateset = Column(String)
    order = Column(Integer)

    language_id = Column(String, ForeignKey("languages.id"))
    origin_lemma_id = Column(
        String, ForeignKey("lemmas.id")
    )  # self-referencing foreign key
    relation = Enum("inheritance", "loaning", name="relation_types")

    # Relationships
    language = relationship("Language", back_populates="lemmas")
    origin_lemma = relationship(
        "Lemma", remote_side=[id]
    )  # self-referencing relationship
    concepts = relationship("Concept", secondary="lemma_concept")
    references = relationship("Reference", secondary="lemma_reference")

    def __repr__(self):
        return f"<Lemma(id='{self.id}', word='{self.word}', gloss='{self.gloss}', native='{self.native}', phonemic='{self.phonemic}', original='{self.original}', notes='{self.notes}', language_id='{self.language_id}', origin_lemma_id='{self.origin_lemma_id}', relation='{self.relation}')>"

# Association tables
class LemmaConcept(Base):
    __tablename__ = "lemma_concept"

    lemma_id = Column(Integer, ForeignKey("lemmas.id"), primary_key=True)
    concept_id = Column(Integer, ForeignKey("concepts.id"), primary_key=True)


class LemmaReference(Base):
    __tablename__ = "lemma_reference"

    lemma_id = Column(Integer, ForeignKey("lemmas.id"), primary_key=True)
    reference_id = Column(Integer, ForeignKey("references.id"), primary_key=True)


# Update Language model to include relationship with Lemma
Language.lemmas = relationship("Lemma", order_by=Lemma.id, back_populates="language")