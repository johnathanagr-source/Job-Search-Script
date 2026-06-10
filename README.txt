Job Search Script

This is a Python script that fetches public Workday job listings, scores them using custom keywords, and exports the results to a CSV file.

Main files:
- main.py: runs the whole script
- config.py: settings and keywords
- models.py: Job data structure
- scoring.py: ranking logic
- workday_scraper.py: fetches jobs from Workday
- exporter.py: writes results to CSV

How to run:
1. Activate the virtual environment.
2. Run: python main.py

Notes:
- Output is written to output/job_matches.csv
- The script is tuned for Ciena Workday listings