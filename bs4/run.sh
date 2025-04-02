#!/bin/bash

echo "Fetching webpage..."
python scrape.py

echo "Parsing HTML..."
python parse.py

echo "Saving to CSV..."
python save.py

echo "Done! Check books.csv for results."
