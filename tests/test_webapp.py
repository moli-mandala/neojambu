#!/usr/bin/env python3
"""
Comprehensive test suite for neojambu webapp performance improvements.
Tests database indexes, session management, and Flask routes.
"""
import pytest
import time
from flask import Flask
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from src.neojambu.app import app, get_session
from src.neojambu.models import Lemma, Language, Reference

class TestDatabaseIndexes:
    """Test that database indexes are properly created and functioning."""
    
    def setup_method(self):
        self.engine = create_engine('sqlite:///data.db')
    
    def test_indexes_exist(self):
        """Test that all required indexes exist."""
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")).fetchall()
            index_names = [row[0] for row in result]
            
            expected_indexes = [
                'idx_lemmas_origin_lemma_id',
                'idx_lemmas_language_id',
                'idx_lemmas_order',
                'idx_lemmas_cognateset'
            ]
            
            for expected in expected_indexes:
                assert expected in index_names, f"Missing index: {expected}"
    
    def test_origin_lemma_id_index_performance(self):
        """Test that origin_lemma_id index improves query performance."""
        with self.engine.connect() as conn:
            # Test query that uses the index
            start = time.time()
            result = conn.execute(text("SELECT COUNT(*) FROM lemmas WHERE origin_lemma_id IS NOT NULL")).scalar()
            end = time.time()
            
            # Should be fast with index (< 0.1 seconds for 300k+ records)
            assert end - start < 0.1, f"Query too slow: {end - start:.4f}s"
            assert result > 0, "Should find reflexes"
    
    def test_language_id_index_performance(self):
        """Test that language_id index improves query performance."""
        with self.engine.connect() as conn:
            # Test query that uses the index
            start = time.time()
            result = conn.execute(text("SELECT COUNT(*) FROM lemmas WHERE language_id = 'san'")).scalar()
            end = time.time()
            
            # Should be fast with index
            assert end - start < 0.05, f"Query too slow: {end - start:.4f}s"
    
    def test_order_index_performance(self):
        """Test that order index improves sorting performance."""
        with self.engine.connect() as conn:
            # Test query that uses the index for ordering
            start = time.time()
            result = conn.execute(text('SELECT * FROM lemmas ORDER BY "order" LIMIT 10')).fetchall()
            end = time.time()
            
            # Should be fast with index
            assert end - start < 0.05, f"Query too slow: {end - start:.4f}s"
            assert len(result) > 0, "Should return results"
    
    def test_cognateset_index_performance(self):
        """Test that cognateset index improves grouping performance."""
        with self.engine.connect() as conn:
            # Test query that uses the index
            start = time.time()
            result = conn.execute(text("SELECT DISTINCT cognateset FROM lemmas LIMIT 10")).fetchall()
            end = time.time()
            
            # Should be fast with index
            assert end - start < 0.05, f"Query too slow: {end - start:.4f}s"
            assert len(result) > 0, "Should return results"


class TestSessionManagement:
    """Test session management and connection pooling."""
    
    def test_get_session_function(self):
        """Test that get_session creates and returns a valid session."""
        session = get_session()
        assert session is not None
        assert hasattr(session, 'query')
        assert hasattr(session, 'close')
        session.close()
    
    def test_session_isolation(self):
        """Test that sessions are properly isolated."""
        session1 = get_session()
        session2 = get_session()
        
        # Should be different session objects
        assert session1 is not session2
        
        session1.close()
        session2.close()
    
    def test_session_query_functionality(self):
        """Test that sessions can perform queries successfully."""
        session = get_session()
        
        try:
            # Test basic query
            count = session.query(Lemma).count()
            assert count > 0, "Should find lemmas in database"
            
            # Test filtered query
            reflexes = session.query(Lemma).filter(Lemma.origin_lemma_id != None).limit(5).all()
            assert len(reflexes) > 0, "Should find reflexes"
            
        finally:
            session.close()
    
    def test_relationship_loading(self):
        """Test that relationships are properly loaded before session close."""
        session = get_session()
        
        try:
            # Get a lemma with eager loading
            lemma = session.query(Lemma).filter(Lemma.origin_lemma_id != None).first()
            if lemma:
                # Access relationship while session is open
                language_name = lemma.language.name if lemma.language else None
                
                # Close session
                session.close()
                
                # Should still be able to access the loaded relationship
                if lemma.language:
                    assert lemma.language.name == language_name
                
        finally:
            if session.is_active:
                session.close()


class TestFlaskRoutes:
    """Test Flask routes for DetachedInstanceError and functionality."""
    
    def setup_method(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_entries_route(self):
        """Test that /entries route works without DetachedInstanceError."""
        response = self.client.get('/entries')
        assert response.status_code == 200
        
        # Should contain entries content
        assert b'entries' in response.data.lower() or b'entry' in response.data.lower()
    
    def test_entries_route_with_pagination(self):
        """Test entries route with pagination."""
        response = self.client.get('/entries?page=1')
        assert response.status_code == 200
    
    def test_reflexes_route(self):
        """Test that /reflexes route works without DetachedInstanceError."""
        response = self.client.get('/reflexes')
        assert response.status_code == 200
    
    def test_reflexes_route_with_pagination(self):
        """Test reflexes route with pagination."""
        response = self.client.get('/reflexes?page=1')
        assert response.status_code == 200
    
    def test_languages_route(self):
        """Test that /languages route works."""
        response = self.client.get('/languages')
        assert response.status_code == 200
    
    def test_references_route(self):
        """Test that /references route works."""
        response = self.client.get('/references')
        assert response.status_code == 200
    
    def test_single_entry_route(self):
        """Test single entry route if entries exist."""
        # First get a valid entry ID
        session = get_session()
        try:
            entry = session.query(Lemma).filter(Lemma.origin_lemma_id == None).first()
            if entry:
                entry_id = entry.id
                session.close()
                
                # Test the route
                response = self.client.get(f'/entries/{entry_id}')
                assert response.status_code == 200
            else:
                session.close()
                pytest.skip("No entries found in database")
        finally:
            if session.is_active:
                session.close()
    
    def test_single_reflex_route(self):
        """Test single reflex route if reflexes exist."""
        # First get a valid reflex ID
        session = get_session()
        try:
            reflex = session.query(Lemma).filter(Lemma.origin_lemma_id != None).first()
            if reflex:
                reflex_id = reflex.id
                session.close()
                
                # Test the route
                response = self.client.get(f'/reflexes/{reflex_id}')
                assert response.status_code == 200
            else:
                session.close()
                pytest.skip("No reflexes found in database")
        finally:
            if session.is_active:
                session.close()
    
    def test_api_routes(self):
        """Test API routes for basic functionality."""
        # Test entries API
        response = self.client.get('/query?type=entries')
        assert response.status_code == 200
        assert response.is_json
        
        # Test languages API
        response = self.client.get('/query?type=languages')
        assert response.status_code == 200
        assert response.is_json
        
        # Test references API
        response = self.client.get('/query?type=references')
        assert response.status_code == 200
        assert response.is_json


class TestPerformanceRegression:
    """Test that performance improvements don't break existing functionality."""
    
    def test_query_filtering(self):
        """Test that search filtering still works."""
        with app.test_client() as client:
            # Test language filtering
            response = client.get('/entries?lang=sanskrit')
            assert response.status_code == 200
            
            # Test word filtering
            response = client.get('/reflexes?word=test')
            assert response.status_code == 200
    
    def test_query_sorting(self):
        """Test that sorting still works."""
        with app.test_client() as client:
            # Test sorting by language
            response = client.get('/entries?sort=asc-lang')
            assert response.status_code == 200
            
            # Test sorting by word
            response = client.get('/reflexes?sort=desc-word')
            assert response.status_code == 200
    
    def test_complex_queries(self):
        """Test complex queries that combine filtering and sorting."""
        session = get_session()
        try:
            # Test entry with reflexes
            entry = session.query(Lemma).filter(Lemma.origin_lemma_id == None).first()
            if entry:
                reflexes = session.query(Lemma).filter_by(origin_lemma_id=entry.id).all()
                # Should work without error
                assert isinstance(reflexes, list)
        finally:
            session.close()


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])