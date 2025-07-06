#!/usr/bin/env python3
"""
Deployment verification script for neojambu webapp.
Ensures all components are working correctly in production.
"""
import os
import sys
import sqlite3
from app import app, get_session
from models import Lemma, Language

def verify_database():
    """Verify database connectivity and data integrity."""
    print("🔍 Verifying database...")
    
    if not os.path.exists('data.db'):
        print("❌ Database file not found!")
        return False
    
    try:
        # Test SQLite connection
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        # Check table existence
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        required_tables = ['lemmas', 'languages', 'references']
        
        for table in required_tables:
            if table not in tables:
                print(f"❌ Missing table: {table}")
                conn.close()
                return False
        
        # Check data counts
        cursor.execute("SELECT COUNT(*) FROM lemmas")
        lemma_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM languages")
        language_count = cursor.fetchone()[0]
        
        conn.close()
        
        if lemma_count < 100000:  # Should have 300k+ lemmas
            print(f"⚠️  Low lemma count: {lemma_count}")
            return False
            
        if language_count < 500:  # Should have 600+ languages
            print(f"⚠️  Low language count: {language_count}")
            return False
        
        print(f"✅ Database verified: {lemma_count} lemmas, {language_count} languages")
        return True
        
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def verify_indexes():
    """Verify that performance indexes exist."""
    print("🔍 Verifying database indexes...")
    
    try:
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        indexes = [row[0] for row in cursor.fetchall()]
        
        required_indexes = [
            'idx_lemmas_origin_lemma_id',
            'idx_lemmas_language_id',
            'idx_lemmas_order',
            'idx_lemmas_cognateset'
        ]
        
        missing_indexes = []
        for index in required_indexes:
            if index not in indexes:
                missing_indexes.append(index)
        
        conn.close()
        
        if missing_indexes:
            print(f"❌ Missing indexes: {missing_indexes}")
            return False
        
        print("✅ All performance indexes verified")
        return True
        
    except Exception as e:
        print(f"❌ Index verification failed: {e}")
        return False

def verify_session_management():
    """Verify session management is working correctly."""
    print("🔍 Verifying session management...")
    
    try:
        session = get_session()
        
        # Test basic query
        count = session.query(Lemma).count()
        if count <= 0:
            print("❌ Session query returned no results")
            session.close()
            return False
        
        # Test relationship loading
        lemma = session.query(Lemma).filter(Lemma.origin_lemma_id != None).first()
        if lemma and lemma.language:
            language_name = lemma.language.name
            session.close()
            
            # Should still be able to access loaded relationship
            test_name = lemma.language.name
            if test_name != language_name:
                print("❌ Relationship loading not working properly")
                return False
        else:
            session.close()
        
        print("✅ Session management verified")
        return True
        
    except Exception as e:
        print(f"❌ Session management verification failed: {e}")
        return False

def verify_flask_app():
    """Verify Flask app can start and handle requests."""
    print("🔍 Verifying Flask application...")
    
    try:
        app.config['TESTING'] = True
        client = app.test_client()
        
        # Test basic routes
        routes_to_test = [
            ('/', 'Home page'),
            ('/entries', 'Entries page'),
            ('/languages', 'Languages page'),
            ('/references', 'References page'),
            ('/query?type=entries', 'Entries API')
        ]
        
        for route, description in routes_to_test:
            response = client.get(route)
            if response.status_code != 200:
                print(f"❌ {description} failed: HTTP {response.status_code}")
                return False
        
        print("✅ Flask application verified")
        return True
        
    except Exception as e:
        print(f"❌ Flask app verification failed: {e}")
        return False

def main():
    """Run all verification checks."""
    print("🚀 Starting NeoJambu deployment verification...")
    print("=" * 50)
    
    checks = [
        verify_database,
        verify_indexes,
        verify_session_management,
        verify_flask_app
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All verification checks passed! Deployment is ready.")
        return 0
    else:
        print("⚠️  Some verification checks failed. Please review and fix issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())