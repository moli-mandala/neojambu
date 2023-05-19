from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker, relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Language(Base):
    __tablename__ = 'languages'

    id = Column(String, primary_key=True)
    name = Column(String)
    glottocode = Column(String)
    long = Column(Float)
    lat = Column(Float)
    clade = Column(String)
    color = Column(String)
    lemma_count = Column(Integer, default=0)
    order = Column(Integer)

    def to_map_marker(self):
        if self.clade in ['MIA', 'OIA'] or 'Old' in self.name:
            return f"""<svg viewBox="0 0 30 30" xmlns="http://www.w3.org/2000/svg"><polygon points="0,15 15,0 30,15 15,30" fill="#{self.color}" stroke="black" stroke-width="2"/></svg>"""
        return f"""<svg viewBox="-2 -2 32 32" xmlns="http://www.w3.org/2000/svg"><circle cx="14" cy="14" r="13" fill="#{self.color}" stroke="black" stroke-width="2"/></svg>"""

    def __repr__(self):
        return f"<Language(id='{self.id}', name='{self.name}', glottocode='{self.glottocode}', long={self.long}, lat={self.lat}, clade='{self.clade}', color='{self.color}')>"

class Concept(Base):
    __tablename__ = 'concepts'

    id = Column(Integer, primary_key=True)
    meaning = Column(String)

class Reference(Base):
    __tablename__ = 'references'

    id = Column(String, primary_key=True)
    short = Column(String)
    source = Column(String)

    def __repr__(self):
        return f"<a href=\"/references/{self.id}\">{self.short}</a>"

class Lemma(Base):
    __tablename__ = 'lemmas'

    id = Column(String, primary_key=True)
    word = Column(String)
    gloss = Column(String)
    native = Column(String)
    phonemic = Column(String)
    original = Column(String)
    notes = Column(String)
    clades = Column(String)

    language_id = Column(String, ForeignKey('languages.id'))
    origin_lemma_id = Column(String, ForeignKey('lemmas.id'))  # self-referencing foreign key
    relation = Enum("inheritance", "loaning", name="relation_types")
    
    # Relationships
    language = relationship("Language", back_populates="lemmas")
    origin_lemma = relationship("Lemma", remote_side=[id])  # self-referencing relationship
    concepts = relationship("Concept", secondary="lemma_concept")
    references = relationship("Reference", secondary="lemma_reference")

    def __repr__(self):
        return f"<Lemma(id='{self.id}', word='{self.word}', gloss='{self.gloss}', native='{self.native}', phonemic='{self.phonemic}', original='{self.original}', notes='{self.notes}', language_id='{self.language_id}', origin_lemma_id='{self.origin_lemma_id}', relation='{self.relation}')>"

# Association tables
class LemmaConcept(Base):
    __tablename__ = 'lemma_concept'
    
    lemma_id = Column(Integer, ForeignKey('lemmas.id'), primary_key=True)
    concept_id = Column(Integer, ForeignKey('concepts.id'), primary_key=True)

class LemmaReference(Base):
    __tablename__ = 'lemma_reference'
    
    lemma_id = Column(Integer, ForeignKey('lemmas.id'), primary_key=True)
    reference_id = Column(Integer, ForeignKey('references.id'), primary_key=True)

# Update Language model to include relationship with Lemma
Language.lemmas = relationship("Lemma", order_by=Lemma.id, back_populates="language")