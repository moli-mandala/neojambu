#!/usr/bin/env python3
"""
Main entry point for the NeoJambu linguistics webapp.
"""

if __name__ == "__main__":
    from src.neojambu.app import app
    app.run(threaded=True, port=2222)