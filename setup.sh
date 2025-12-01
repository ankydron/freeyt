#!/bin/bash
python3 -m venv venv || true
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null || true
pip install -q -r requirements.txt 2>/dev/null
python3 -m py_compile app.py
echo "Setup complete!"
