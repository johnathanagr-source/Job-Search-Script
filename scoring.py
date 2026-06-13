from datetime import datetime

def score_job(job, title_keywords, location_keywords, optical_keywords, exclude_keywords):
    text = f"{job.title} {job.location} {job.description}".lower()
    score = 0

    if any(k.lower() in job.title.lower() for k in title_keywords):
        score += 100
    else:
        score -= 100

    if any(k.lower() in job.location.lower() for k in location_keywords):
        score += 100
    else:
        score -= 100

    score += sum(10 for k in optical_keywords if k.lower() in text)

    score -= sum(50 for k in exclude_keywords if k.lower() in text)
       
    return score

def parse_date(date_str):
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except:
        return datetime.min