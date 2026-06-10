from config import TITLE_KEYWORDS, LOCATION_KEYWORDS, OPTICAL_KEYWORDS, EXCLUDE_KEYWORDS, OUTPUT_FILE
from workday_scraper import fetch_workday_jobs
from scoring import score_job, parse_date
from exporter import export_csv

def main():
    jobs = fetch_workday_jobs()

    for job in jobs:
        job.score = score_job(
            job,
            TITLE_KEYWORDS,
            LOCATION_KEYWORDS,
            OPTICAL_KEYWORDS,
            EXCLUDE_KEYWORDS
        )

    jobs = sorted(
        jobs,
        key=lambda j: (j.score, parse_date(j.posted_date)),
        reverse=True
    )

    export_csv(jobs, OUTPUT_FILE)
    print(f"Saved {len(jobs)} jobs to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()