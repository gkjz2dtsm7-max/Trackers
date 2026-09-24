"""
Roach Roundup — Live Data Trackers
Main update script. Runs every 6 hours via GitHub Actions.

Phase 1: Federal PBM reform bills from congress.gov API.
Future phases: Mississippi bills, FEC data, Federal Register rules, etc.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from jinja2 import Environment, FileSystemLoader

# --- Config ---------------------------------------------------------------

CONGRESS_API_KEY = os.environ.get("CONGRESS_API_KEY", "")
CONGRESS_API_BASE = "https://api.congress.gov/v3"

# Which Congress to watch. 119th Congress: Jan 2025 - Jan 2027.
# Update this when a new Congress begins.
CURRENT_CONGRESS = 119

# Keywords that flag a bill as PBM-relevant. Case-insensitive substring match
# on the bill title.
PBM_KEYWORDS = [
    "pharmacy benefit manager",
    "pharmacy benefit managers",
    "pbm ",
    "prescription drug pric",
    "drug pricing transparency",
    "spread pricing",
]

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
TEMPLATE_DIR = ROOT / "templates"
REQUEST_TIMEOUT_SECONDS = 30
PAGE_SIZE = 250


# --- Congress.gov client --------------------------------------------------

def cg_get(path, params=None):
    """Call the congress.gov API and return parsed JSON."""
    if not CONGRESS_API_KEY:
        print("ERROR: CONGRESS_API_KEY is not set. Add it as a GitHub Secret.")
        sys.exit(1)

    req_params = {
        "api_key": CONGRESS_API_KEY,
        "format": "json",
    }
    if params:
        req_params.update(params)

    url = f"{CONGRESS_API_BASE}{path}"
    response = requests.get(url, params=req_params, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()


def is_pbm_relevant(title):
    if not title:
        return False
    normalized = title.lower()
    return any(keyword in normalized for keyword in PBM_KEYWORDS)


def fetch_all_bills_for_congress(congress):
    bills = []
    offset = 0
    while True:
        payload = cg_get(
            f"/bill/{congress}",
            {
                "limit": PAGE_SIZE,
                "offset": offset,
            },
        )
        page_bills = payload.get("bills", [])
        bills.extend(page_bills)

        if len(page_bills) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    return bills


def fetch_bill_details(congress, bill_type, bill_number):
    payload = cg_get(f"/bill/{congress}/{bill_type}/{bill_number}")
    return payload.get("bill", {})


def normalize_bill_row(bill, details):
    sponsor = details.get("sponsors", [{}])[0] if details.get("sponsors") else {}
    latest_action = details.get("latestAction", {}) or {}

    return {
        "bill_id": f"{bill.get('type', '').upper()} {bill.get('number', '')}".strip(),
        "title": bill.get("title", ""),
        "url": bill.get("url", ""),
        "sponsor_name": sponsor.get("fullName", ""),
        "sponsor_party": sponsor.get("party", ""),
        "sponsor_state": sponsor.get("state", ""),
        "latest_action_date": latest_action.get("actionDate", ""),
        "latest_action_text": latest_action.get("text", ""),
        "cosponsor_count": details.get("cosponsors", {}).get("count", 0),
    }


def build_pbm_tracker():
    bills = fetch_all_bills_for_congress(CURRENT_CONGRESS)
    matching_bills = [bill for bill in bills if is_pbm_relevant(bill.get("title", ""))]

    rows = []
    for bill in matching_bills:
        bill_type = bill.get("type")
        bill_number = bill.get("number")
        if not bill_type or not bill_number:
            continue

        details = fetch_bill_details(CURRENT_CONGRESS, bill_type, bill_number)
        rows.append(normalize_bill_row(bill, details))

    rows.sort(
        key=lambda row: (
            row.get("latest_action_date") or "",
            row.get("bill_id") or "",
        ),
        reverse=True,
    )

    return {
        "title": "Federal PBM Reform Bills",
        "subtitle": f"{CURRENT_CONGRESS}th Congress · congress.gov",
        "rows": rows,
    }


def write_json(trackers_payload):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = DATA_DIR / "trackers.json"
    output_path.write_text(json.dumps(trackers_payload, indent=2), encoding="utf-8")


def render_html(trackers_payload):
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    template = env.get_template("index.html")

    html = template.render(
        updated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        trackers=trackers_payload,
    )
    (DOCS_DIR / "index.html").write_text(html, encoding="utf-8")


def main():
    pbm_tracker = build_pbm_tracker()
    trackers_payload = {"federal_pbm_bills": pbm_tracker}
    write_json(trackers_payload)
    render_html(trackers_payload)
    print(f"Updated trackers successfully. Rows: {len(pbm_tracker['rows'])}")


if __name__ == "__main__":
    main()
