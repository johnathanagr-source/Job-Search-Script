import requests
from models import Job
from config import BASE_URL

def fetch_workday_jobs():
    url = "https://ciena.wd5.myworkdayjobs.com/wday/cxs/ciena/Careers/jobs"

    payload = {
        "appliedFacets": {},
        "limit": 20,
        "offset": 0,
        "searchText": ""
    }

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": BASE_URL,
        "Referer": f"{BASE_URL}/Careers/",
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.post(url, json=payload, headers=headers, timeout=30)

    if r.status_code != 200:
        raise Exception(f"Workday request failed: {r.status_code} - {r.text[:500]}")

    data = r.json()

    jobs = []
    for item in data.get("jobPostings", []):
        path = item.get("externalPath", "")
        full_url = path if path.startswith("http") else BASE_URL + path

        jobs.append(Job(
            title=item.get("title", ""),
            location=item.get("locationsText", ""),
            posted_date=item.get("postedOn", ""),
            description=item.get("shortDescription", ""),
            url=full_url
        ))
    return jobs