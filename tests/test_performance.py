#!/usr/bin/env python3
"""
Performance testing script for the neojambu webapp optimizations.
"""
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.neojambu.models import Lemma, Language

def test_database_indexes():
    """Test database query performance with new indexes."""
    print("Testing database indexes...")
    
    engine = create_engine('sqlite:///data.db')
    with engine.connect() as conn:
        # Test index performance on origin_lemma_id
        start = time.time()
        result = conn.execute(text('SELECT COUNT(*) FROM lemmas WHERE origin_lemma_id IS NOT NULL')).scalar()
        end = time.time()
        print(f'Reflexes count query: {end - start:.4f}s, found {result} reflexes')
        
        # Test index performance on language_id
        start = time.time()
        result = conn.execute(text('SELECT COUNT(*) FROM lemmas WHERE language_id = "hin"')).scalar()
        end = time.time()
        print(f'Language filter query: {end - start:.4f}s, found {result} lemmas')
        
        # Test ordering with index
        start = time.time()
        result = conn.execute(text('SELECT * FROM lemmas ORDER BY "order" LIMIT 10')).fetchall()
        end = time.time()
        print(f'Ordered query: {end - start:.4f}s, fetched {len(result)} lemmas')

def test_session_management():
    """Test new session management implementation."""
    print("\nTesting session management...")
    
    engine = create_engine(
        'sqlite:///data.db',
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={'check_same_thread': False}
    )
    Session = sessionmaker(bind=engine)
    
    def get_session():
        return Session()
    
    # Test session creation and cleanup
    start = time.time()
    session = get_session()
    count = session.query(Lemma).filter(Lemma.origin_lemma_id != None).count()
    session.close()
    end = time.time()
    print(f'Session query test: {end - start:.4f}s, found {count} reflexes')
    print('Session management: OK')

def test_complex_queries():
    """Test complex queries that benefit from indexes."""
    print("\nTesting complex queries...")
    
    engine = create_engine('sqlite:///data.db')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Test entry page query (benefits from origin_lemma_id index)
        start = time.time()
        reflexes = session.query(Lemma).filter_by(origin_lemma_id="1").all()
        end = time.time()
        print(f'Entry reflexes query: {end - start:.4f}s, found {len(reflexes)} reflexes')
        
        # Test language page query (benefits from language_id index)
        start = time.time()
        lemmas = session.query(Lemma).filter_by(language_id="san").limit(50).all()
        end = time.time()
        print(f'Language lemmas query: {end - start:.4f}s, found {len(lemmas)} lemmas')
        
        # Test cognateset grouping (benefits from cognateset index)
        start = time.time()
        cognatesets = session.query(Lemma.cognateset).distinct().limit(10).all()
        end = time.time()
        print(f'Cognateset grouping: {end - start:.4f}s, found {len(cognatesets)} sets')
        
    finally:
        session.close()

if __name__ == "__main__":
    print("=== Performance Testing ===")
    test_database_indexes()
    test_session_management()
    test_complex_queries()
    print("\n=== Testing Complete ===")