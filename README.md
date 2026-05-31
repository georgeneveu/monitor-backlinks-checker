# Monitor Backlinks Checker 🔗
Monitor backlinks checker is a fast async Python tool for checking backlink status from Excel files. It verifies URLs (Live, Forbidden, Dead) using concurrent requests and exports results into organized Excel batches. Ideal for SEO audits, link monitoring, and cleaning backlink profiles efficiently.

## ⚡ What this tool does (important)
For each row in your Excel file, it performs **two checks**:

### 1. Page availability check
- Confirms the backlink URL is accessible
- Example: `https://medium.com/how-to-write-article/`
- Status codes:
  - `200` → page is alive
  - `403/404/500` → page is broken or blocked

### 2. Backlink presence check
- Downloads the HTML of the page
- Searches for your domain inside the page source
- Example domain: `essay-website.com`

Results:
- ✅ **Backlink FOUND** → domain exists in page HTML
- ❌ **Backlink MISSING** → page exists but link removed or not present

## 📥 Input File Format
The tool reads an Excel file named: links.xlsx

### 📌 Required columns

| Column Name | Description |
|-------------|-------------|
| Project     | Your website/domain (e.g. essay-website.com) |
| Backlink    | URL where backlink should exist |

### 📊 Example input

| Project | Backlink |
|----------|----------|
| essay-website.com | https://medium.com/how-to-write-article |
| essay-website.com | https://wordpress.com/blog/sample-post |


## 🧠 How it processes data

For this row:
| Project | Backlink |
|----------|----------|
| essay-website.com | https://medium.com/how-to-write-article |

The tool:

1. Opens the Medium page
2. Checks if page returns `200 OK`
3. Downloads HTML content
4. Searches for: essay-website.com

5. Returns result:
- Backlink FOUND
- Backlink MISSING
- or Page DEAD

## 📤 Output

Results are saved into timestamped folders:
batch_1_20260124_153000/
batch_2_20260124_153000/

Each batch contains: `results.xlsx`

### 📊 Output format

| Project Domain | Backlink URL | Status | Status Code |
|----------------|--------------|--------|-------------|
| essay-website.com | https://medium.com/... | Backlink FOUND | 200 |
| essay-website.com | https://medium.com/... | Backlink MISSING | 200 |

## 🚀 Installation

Install dependencies:
```bash
pip install pandas aiohttp openpyxl
