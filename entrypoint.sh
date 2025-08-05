#!/bin/bash
python3 src/init_db.py
uvicorn src.main:app --host 0.0.0.0 --port 8000