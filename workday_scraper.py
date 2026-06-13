import requests
import time
from urllib.parse import urljoin
from models import Job
from bs4 import BeautifulSoup
from config import LOCATION_KEYWORDS, SITES

def _headers(base_url, careers_url):
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": base_url,
        "Referer": careers_url if careers_url.endswith("/") else careers_url + "/",
        "User-Agent": "Mozilla/5.0",
    }

def _fetch_page(api_url, headers, limit, offset, applied_facets, retries=3):
    payload = {
        "appliedFacets": applied_facets or {},
        "limit": limit,
        "offset": offset,
        "searchText": "",
    }
    for attempt in range(retries):
        try:
            r = requests.post(api_url, json=payload, headers=headers, timeout=(5, 30))
            r.raise_for_status()
            return r.json()
        except requests.exceptions.Timeout:
            if attempt == retries - 1:
                return None
            time.sleep(2 * (attempt + 1))

def _iter_dicts(obj):
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from _iter_dicts(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from _iter_dicts(item)

def _find_location_facet(data, preferred_location):
    preferred = (preferred_location or "").strip().lower()
    for node in _iter_dicts(data.get("facets", [])):
        facet_parameter = node.get("facetParameter")
        values = node.get("values")
        if not isinstance(values, list):
            continue
        for value in values:
            if not isinstance(value, dict):
                continue
            descriptor = str(value.get("descriptor", "")).strip()
            if not descriptor:
                continue
            desc_lower = descriptor.lower()
            if preferred and desc_lower == preferred:
                return facet_parameter, value.get("id")
    return None

def _fetch_html(url, retries=3):
    for attempt in range(retries):
        try:
            r = requests.get(url, timeout=(5, 30))
            r.raise_for_status()
            return r.text
        except requests.exceptions.RequestException:
            if attempt == retries - 1:
                return ""
            time.sleep(2 * (attempt + 1))

def _fallback_location_facet(data):
    candidates = []
    for node in _iter_dicts(data.get("facets", [])):
        facet_parameter = node.get("facetParameter")
        values = node.get("values")
        if not isinstance(values, list):
            continue
        for value in values:
            if not isinstance(value, dict):
                continue
            descriptor = str(value.get("descriptor", "")).strip()
            if not descriptor:
                continue
            candidates.append((facet_parameter, descriptor, value.get("id")))
    for facet_parameter, descriptor, value_id in candidates:
        text = descriptor.lower()
        if "canada" in text or "ottawa" in text or "remote" in text:
            return facet_parameter, value_id
    return None

def _matches_keywords(location):
    if not LOCATION_KEYWORDS:
        return True
    loc = (location or "").lower()
    return any(k.lower() in loc for k in LOCATION_KEYWORDS)

def fetch_workday_jobs(site):
    careers_url = site["careers_url"]
    base_url = site["base_url"]
    tenant = site["tenant"]
    path = site["path"]
    preferred_location = site.get("preferred_location", "Canada")

    api_url = f"{base_url}/wday/cxs/{tenant}/{path}/jobs"
    headers = _headers(base_url, careers_url)
    jobs = []
    limit = 3
    offset = 0

    first_data = _fetch_page(api_url, headers, limit, 0, {})
    if not first_data:
        return jobs
    
    location_facet = _find_location_facet(first_data, preferred_location) or _fallback_location_facet(first_data)

    if location_facet:
        facet_key, facet_id = location_facet
        applied_facets = {facet_key: [facet_id]}
    else:
        applied_facets = {}

    seen_pages = set()

    while True:
        data = first_data if offset == 0 else _fetch_page(api_url, headers, limit, offset, applied_facets)
        if not data:
            break

        postings = data.get("jobPostings", [])
        sig = tuple(item.get("externalPath", "") for item in postings)

        print("offset", offset, "count", len(postings))

        if sig in seen_pages:
            print("repeated page, stopping")
            break
        seen_pages.add(sig)

        for item in postings:
            path = item.get("externalPath", "")
            if not path or path in seen_pages:
                continue
            seen_pages.add(path)

            location = item.get("locationsText", "")
            if not _matches_keywords(location):
                continue

            job_url = urljoin(careers_url.rstrip("/") + "/", path.lstrip("/"))
            #print("job", item.get("title"), job_url)

            html = _fetch_html(job_url)
            if not html:
                continue

            soup = BeautifulSoup(html, "html.parser")
            desc_tag = soup.find("meta", attrs={"property": "og:description"})
            description = desc_tag.get("content", "").strip() if desc_tag else ""

            jobs.append(Job(
                title=item.get("title", ""),
                location=location,
                posted_date=item.get("postedOn", ""),
                description=description,
                url=job_url,
            ))

        offset += limit


    return jobs

def fetch_all_workday_jobs():
    all_jobs = []
    for site in SITES:
        all_jobs.extend(fetch_workday_jobs(site))
    return all_jobs