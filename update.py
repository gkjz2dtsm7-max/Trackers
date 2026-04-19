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

# --- Congress.gov client --------------------------------------------------

def cg_get(path, params=None):
    """Call the congress.gov API and return parsed JSON."""
    if not CONGRESS_API_KEY:
        print("ERROR: CONGRESS_API_KEY is not set. Add it as a GitHub Secret.")
        sys.exit(1)

    url = f"{CONGRESS_API_BASE}{path}"
    params = {​​​​​​​​​​​​​​​​
