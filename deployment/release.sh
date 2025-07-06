#!/bin/bash
# Heroku release script for neojambu webapp
# This runs during deployment to set up the database

set -e

echo "=== NeoJambu Release Process ==="

# Check if we're in a Heroku environment
if [ -n "$DYNO" ]; then
    echo "Running in Heroku environment"
    
    # Download the latest database if it doesn't exist
    if [ ! -f "data.db" ]; then
        echo "Downloading database..."
        curl -L https://github.com/moli-mandala/data/releases/latest/download/data.db -o data.db
        echo "Database downloaded successfully"
    else
        echo "Database already exists"
    fi
    
    # Verify database integrity
    if uv run python -c "
import sqlite3
try:
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM lemmas')
    count = cursor.fetchone()[0]
    print(f'Database verification: {count} lemmas found')
    conn.close()
    if count > 0:
        print('Database integrity check: PASSED')
    else:
        print('Database integrity check: FAILED - No data found')
        exit(1)
except Exception as e:
    print(f'Database integrity check: FAILED - {e}')
    exit(1)
"; then
        echo "Database integrity verified"
    else
        echo "Database integrity check failed"
        exit 1
    fi
    
else
    echo "Running in local environment - skipping Heroku-specific setup"
fi

echo "=== Release process completed successfully ==="