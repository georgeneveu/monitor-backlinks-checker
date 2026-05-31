import os
import re
import asyncio
import pandas as pd
import aiohttp

from datetime import datetime
from aiohttp import ClientTimeout


# =========================================================
# CONFIG
# =========================================================

INPUT_FILE = "links.xlsx"

BATCH_SIZE = 1000
CONCURRENCY = 100
TIMEOUT_SECONDS = 20

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M%S")


# =========================================================
# NORMALIZE
# =========================================================

def normalize_url(url):
    url = str(url).strip()
    if not url:
        return None

    if not re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', url):
        url = "https://" + url

    return url


# =========================================================
# EXCEL PARSER
# =========================================================

def build_pairs_from_df(df):
    """
    Columns expected:
    - Project (your domain)
    - Backlink (page where backlink should exist)
    """

    pairs = []
    df = df.fillna("")

    for _, row in df.iterrows():
        project = str(row.get("Project", "")).strip()
        backlink = str(row.get("Backlink", "")).strip()

        if not project or not backlink:
            continue

        pairs.append((project, normalize_url(backlink)))

    return pairs


# =========================================================
# CORE CHECK FUNCTION
# =========================================================

async def check_backlink(session, project_domain, backlink_url):
    """
    1. Check if backlink page is alive
    2. Check if project domain exists inside HTML
    """

    try:
        async with session.get(backlink_url, allow_redirects=True) as resp:
            status = resp.status
            html = await resp.text(errors="ignore")

        # -------------------------
        # 1. PAGE CHECK
        # -------------------------
        if status != 200:
            return project_domain, backlink_url, "Dead Page", status

        # -------------------------
        # 2. BACKLINK CHECK
        # -------------------------
        if project_domain.lower() in html.lower():
            return project_domain, backlink_url, "Backlink FOUND", 200
        else:
            return project_domain, backlink_url, "Backlink MISSING", 200

    except asyncio.TimeoutError:
        return project_domain, backlink_url, "Timeout", "Timeout"
    except Exception as e:
        return project_domain, backlink_url, "Error", str(e)


# =========================================================
# SAVE RESULTS
# =========================================================

def save_batch(batch_num, results):
    folder = f"batch_{batch_num}_{RUN_ID}"
    os.makedirs(folder, exist_ok=True)

    df = pd.DataFrame(results, columns=[
        "Project Domain",
        "Backlink URL",
        "Status",
        "Status Code"
    ])

    df.to_excel(f"{folder}/results.xlsx", index=False)

    print(f"\n💾 Saved batch {batch_num} → {folder}")
    print(f"Total: {len(results)}\n")


# =========================================================
# MAIN RUNNER
# =========================================================

async def run_checker(pairs):
    timeout = ClientTimeout(total=TIMEOUT_SECONDS)
    connector = aiohttp.TCPConnector(limit=CONCURRENCY)

    results = []
    batch_num = 1

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:

        tasks = [
            check_backlink(session, project, url)
            for project, url in pairs
        ]

        for i, task in enumerate(asyncio.as_completed(tasks), start=1):

            result = await task
            results.append(result)

            print(f"[{i}/{len(pairs)}] {result[1]} → {result[2]}")

            if i % BATCH_SIZE == 0:
                save_batch(batch_num, results)
                results = []
                batch_num += 1

        # final save
        if results:
            save_batch(batch_num, results)

    print("\nAll done ✅")


# =========================================================
# RUN
# =========================================================

if __name__ == "__main__":

    df = pd.read_excel(INPUT_FILE, dtype=str)

    pairs = build_pairs_from_df(df)

    asyncio.run(run_checker(pairs))
