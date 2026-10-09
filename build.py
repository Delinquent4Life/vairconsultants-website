"""Generate one HTML file per page so each service has its own address for Google.

Run after every change to index.html or routes.json:   python3 build.py
index.html is the source and the home page. This script writes:
  <page path>/index.html  for every entry in routes.json
  news/<post>/index.html  for every published news post
  sitemap.xml, robots.txt
"""
import datetime, html, json, os, re, shutil
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = "https://vairconsultants.com"
src_path = os.path.join(ROOT, "index.html")
routes = json.load(open(os.path.join(ROOT, "routes.json"), encoding="utf-8"))
src = open(src_path, encoding="utf-8").read()

# keep the route table inside index.html in step with routes.json
table = json.dumps([{k: x[k] for k in ("r", "p", "t", "d")} for x in routes], ensure_ascii=False)
src = re.sub(r'(<script id="routes" type="application/json">).*?(</script>)',
             lambda m: m.group(1) + table.replace("</", "<\\/") + m.group(2), src, count=1, flags=re.S)

def set_head(page, title, desc, url, og_type="website"):
    a = lambda s: html.escape(s, quote=True)
    page = re.sub(r"<title>.*?</title>", "<title>" + html.escape(title) + "</title>", page, count=1, flags=re.S)
    page = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="' + a(desc) + '">', page, count=1)
    page = re.sub(r'<link rel="canonical" href="[^"]*">', '<link rel="canonical" href="' + a(url) + '">', page, count=1)
    page = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="' + a(title) + '">', page, count=1)
    page = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="' + a(desc) + '">', page, count=1)
    page = re.sub(r'<meta property="og:url" content="[^"]*">', '<meta property="og:url" content="' + a(url) + '">', page, count=1)
    page = re.sub(r'<meta property="og:type" content="[^"]*">', '<meta property="og:type" content="' + og_type + '">', page, count=1)
    return page

def show(page, route):
    """Mark the right section visible in the file itself, so it shows even before the script runs."""
    return re.sub(
        r'<div class="page([^"]*)" data-page="' + re.escape(route) + '">',
        lambda m: '<div class="page' + m.group(1) + ' on" data-page="' + route + '">', page, count=1)

def write(path, page):
    d = os.path.join(ROOT, path.strip("/"))
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(page)

# remove pages generated last time
for old in open(os.path.join(ROOT, ".generated"), encoding="utf-8").read().split() if os.path.exists(os.path.join(ROOT, ".generated")) else []:
    shutil.rmtree(os.path.join(ROOT, old), ignore_errors=True)
generated, urls = [], []

home = next(x for x in routes if x["r"] == "")
src = set_head(src, home["t"], home["d"], SITE + "/")
open(src_path, "w", encoding="utf-8").write(src)
urls.append(SITE + "/")

for x in routes:
    if x["r"] == "": continue
    write(x["p"], show(set_head(src, x["t"], x["d"], SITE + x["p"]), x["r"]))
    generated.append(x["p"].strip("/").split("/")[0]); urls.append(SITE + x["p"])

# news posts that are already published (Sint Maarten date)
today = datetime.datetime.now(ZoneInfo("America/Lower_Princes")).date().isoformat()
block = re.search(r"const POSTS = \[(.*?)\n\];", src, re.S).group(1)
for m in re.finditer(r'date:\s*"(\d{4}-\d{2}-\d{2})".*?title:\s*"((?:[^"\\]|\\.)*)".*?text:\s*"((?:[^"\\]|\\.)*)"', block, re.S):
    date, title, text = m.group(1), json.loads('"' + m.group(2) + '"'), json.loads('"' + m.group(3) + '"')
    if date > today: continue
    slug = date + "-" + re.sub(r"^-|-$", "", re.sub(r"[^a-z0-9]+", "-", title.lower()))
    desc = text.split("\n\n")[0]
    desc = desc if len(desc) <= 160 else desc[:157].rsplit(" ", 1)[0] + "…"
    page = set_head(src, title + " | V.A.I.R Consultants", desc, SITE + "/news/" + slug + "/", "article")
    write("/news/" + slug + "/", show(page, "news/post"))
    urls.append(SITE + "/news/" + slug + "/")

open(os.path.join(ROOT, ".generated"), "w", encoding="utf-8").write("\n".join(sorted(set(generated))) + "\n")
open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join("  <url><loc>" + u + "</loc></url>\n" for u in urls) + "</urlset>\n")
open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write("User-agent: *\nAllow: /\n\nSitemap: " + SITE + "/sitemap.xml\n")
print(len(urls), "pages; today", today)
