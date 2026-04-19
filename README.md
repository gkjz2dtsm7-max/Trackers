# Roach Roundup — Live Data Trackers

Live, auto-updating data trackers pulling from federal government sources.
Built and maintained by [Rebecca Bruckner](mailto:Rebecca@RoachRoundup.com) for
**Roach Roundup** investigative reporting.

## What's here (Phase 1)

- **Federal PBM reform bills** — live feed from congress.gov API, refreshed
  every 6 hours. Tracks pharmacy benefit manager legislation, drug pricing
  transparency bills, and spread-pricing reform across the 119th Congress.

Future phases add Mississippi state bills, FEC campaign finance, Federal
Register rule filings (HHS + Treasury), OCC/FDIC/CFPB enforcement actions,
and lobbying disclosures.

## Live site

Deployed to GitHub Pages. After setup completes, the tracker will be live at:

`https://gkjz2dtsm7-max.github.io/Trackers/`

Eventually moves to `trackers.roachroundup.com`.

## Setup (one-time)

### 1. Get a congress.gov API key

1. Go to <https://api.data.gov/signup>
2. Fill in the form (purpose: "Journalism / Roach Roundup trackers")
3. Your API key arrives in your inbox immediately
4. Rate limit: 1,000 requests/hour — more than enough

### 2. Add the key as a GitHub Secret

1. In this repo: **Settings** → **Secrets and variables** → **Actions**
2. Tap **New repository secret**
3. Name: `CONGRESS_API_KEY`
4. Value: paste your key
5. Tap **Add secret**

### 3. Enable GitHub Pages

1. **Settings** → **Pages**
2. Under "Build and deployment," set **Source** to **GitHub Actions**
3. Save

### 4. Trigger the first run

1. Go to **Actions** tab
2. Click **Update Trackers** in the left sidebar
3. Click **Run workflow** → **Run workflow** (green button)
4. Wait ~2 minutes. When the check turns green, your site is live.

## How it runs

Every 6 hours, GitHub Actions:

1. Pulls the latest bills from congress.gov
2. Filters for PBM-relevant keywords
3. Fetches detail (sponsor, cosponsors, latest action) for each match
4. Writes JSON to `data/` and HTML to `docs/`
5. Commits the changes back to this repo
6. Deploys `docs/` to GitHub Pages

## Project structure

