import csv
import os

# Export the scored jobs to a CSV file
def export_csv(jobs, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "location", "posted_date", "score", "url"])
        for job in jobs:
            writer.writerow([job.title, job.location, job.posted_date, job.score, job.url])