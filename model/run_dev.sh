#!/bin/bash

# Navigate to the script's directory
cd "$(dirname "$0")"

echo "Checking dependencies..."
pip install -r model/requirements.txt

echo "Starting DivyaDhrishti on port 5001..."
python3 model/app.py
