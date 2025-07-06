import timeit
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from models import Language, Lemma

# Set up
engine = create_engine('sqlite:///data.db')
Session = sessionmaker(bind=engine)

def query_lemmas(lang_id: str = 'all'):
    session = Session()

    # Time the query
    start_time = timeit.default_timer()
    if lang_id == 'all':
        lemmas = session.query(Lemma).limit(200).all()
    else:
        lemmas = session.query(Lemma).filter(Lemma.language_id == lang_id).all()
    end_time = timeit.default_timer()

    session.close()

    return end_time - start_time

# Run the query and print the time it took
print(f"Query time for all lemmas:              {query_lemmas():.5f} seconds")
print(f"Query time for all 'H' lemmas:          {query_lemmas('H'):.5f} seconds")
print(f"Query time for all 'Indo-Aryan' lemmas: {query_lemmas('Indo-Aryan'):.5f} seconds")